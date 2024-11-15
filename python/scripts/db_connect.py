from config import MYSQL_CONFIG, SSL_KEY_BASE64
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import base64
from sqlalchemy import create_engine
from datetime import datetime

def get_connection_pool():
    db_config = MYSQL_CONFIG.copy()
    
    # Add SSL configuration if available
    if SSL_KEY_BASE64:
        ssl_cert = base64.b64decode(SSL_KEY_BASE64).decode('ascii')
        db_config['ssl_ca'] = ssl_cert
        db_config['ssl_verify_cert'] = False

    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
        print("Successfully created the connection pool.")
        return pool
    except mysql.connector.Error as err:
        print(f"Error creating the connection pool: {err}")
        return None

def execute_query(pool, query, params=None):
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            with pool.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    result = cursor.fetchall()
                    return result
        except mysql.connector.Error as err:
            print(f"Error executing query (attempt {retries + 1}): {err}")
            retries += 1
            if retries == max_retries:
                raise
            # Wait for 1 second before retrying
            import time
            time.sleep(1)

def fetch_predict_data(pool):
    query = """
        SELECT 
            c.CompanyName,
            p.CompanyID,
            p.Year,
            ROUND(p.Environmental, 2) AS Environmental_Score,
            ROUND(p.Social, 2) AS Social_Score,
            ROUND(p.Governance, 2) AS Governance_Score,
            ROUND(p.ESG_Score, 2) AS ESG_Score,
            p.Data_Type
        FROM esg_predictions p
        INNER JOIN company_info c ON p.CompanyID = c.CompanyID
        ORDER BY c.CompanyName, p.Year
    """
    return execute_query(pool, query)

def fetch_company_info(pool):
    query = "SELECT * FROM company_info"
    return execute_query(pool, query)

def fetch_environmental_data(pool):
    query = "SELECT * FROM environment"

    return execute_query(pool, query)

def fetch_ESG_data(pool):
    query = "SELECT * FROM esg_scores"

    return execute_query(pool, query)

def fetch_ESG_financial_data(pool):
    query = "SELECT CompanyID, Final_ESG_Score FROM esg_scores WHERE ReportYear = 2023 AND CompanyID IN (1, 2, 3, 4, 5, 6, 7, 8)"

    return execute_query(pool, query)

def fetch_social_data(pool):
    query = "SELECT * FROM social"

    return execute_query(pool, query)


def fetch_ESG_score_2023(pool):
    query = "SELECT CompanyID, Final_ESG_Score FROM esg_scores WHERE ReportYear = 2023 AND CompanyID IN (1, 2, 3, 4, 5, 6, 7, 8)"
    return execute_query(pool, query)

def fetch_2023_finances(pool):
    query = "SELECT * FROM esg_fin"
    return execute_query(pool, query)

def fetch_governance_data(pool):
    query = "SELECT * FROM governance"
    return execute_query(pool, query)

def update_table(pool, df, table_name):
    try:
        # Create SQLAlchemy engine using config
        connection_string = (
            f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}"
            f"@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
        )
        engine = create_engine(connection_string)
        
        # Convert float64 columns to float
        float_columns = df.select_dtypes(include=['float64']).columns
        df[float_columns] = df[float_columns].astype(float)

        # Add update_time column
        df['update_time'] = datetime.now()

        # Write the DataFrame to the specified table
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Successfully updated the {table_name} table in the database.")
        
    except Exception as e:
        print(f"An error occurred while updating the {table_name} table: {str(e)}")
    finally:
        engine.dispose()



def update_predict_table(pool, final_df):
    try:
        # Create SQLAlchemy engine using MYSQL_CONFIG
        connection_string = (
            f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}"
            f"@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
        )
        engine = create_engine(connection_string)
        
        # Rename 'ESG Score' to 'ESG_Score' if it exists
        if 'ESG Score' in final_df.columns:
            final_df = final_df.rename(columns={'ESG Score': 'ESG_Score'})

        # Convert float64 columns to float
        float_columns = final_df.select_dtypes(include=['float64']).columns
        final_df[float_columns] = final_df[float_columns].astype(float)

        # Add update_time column
        final_df['update_time'] = datetime.now()

        # Write the DataFrame to the 'esg_predictions' table
        final_df.to_sql('esg_predictions', engine, if_exists='replace', index=False)
        print("Successfully updated the esg_predictions table in the database.")
    except Exception as e:
        print(f"An error occurred while updating the esg_predictions table: {str(e)}")
    finally:
        # Close the database connection
        engine.dispose()

def fetch_env_score_data(pool):
    query = """
        SELECT 
            e.CompanyID,
            c.CompanyName,
            e.ReportYear,
            e.EnergyConsumption_score,
            e.GHGEmissions_score,
            e.WaterUsage_score,
            e.WasteGenerated_score
        FROM env_score e
        JOIN company_info c ON e.CompanyID = c.CompanyID
        ORDER BY c.CompanyName, e.ReportYear
    """
    return execute_query(pool, query)
