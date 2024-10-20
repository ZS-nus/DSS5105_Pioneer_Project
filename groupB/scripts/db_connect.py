import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import base64
from sqlalchemy import create_engine
from datetime import datetime

def connect_to_db():
    load_dotenv()

    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'pool_size': 10,
        'pool_name': 'mypool',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_general_ci'
    }

    ssl_key_base64 = os.getenv('SSL_KEY_BASE64')
    if ssl_key_base64:
        ssl_cert = base64.b64decode(ssl_key_base64).decode('ascii')
        db_config['ssl_ca'] = ssl_cert
        db_config['ssl_verify_cert'] = False

    print(f"Connecting to {db_config['host']}:{db_config['port']} as {db_config['user']}")

    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
        print("Successfully connected to the database.")
        return pool
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
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

def fetch_company_info(pool):
    query = "SELECT * FROM company_info"
    return execute_query(pool, query)

def fetch_environmental_data(pool):
    query = "SELECT * FROM environment"

    return execute_query(pool, query)

def fetch_ESG_data(pool):
    query = "SELECT * FROM esg_scores"

    return execute_query(pool, query)


def fetch_social_data(pool):
    query = "SELECT * FROM social"

    return execute_query(pool, query)


def fetch_governance_data(pool):
    query = "SELECT * FROM governance"
    return execute_query(pool, query)


def update_table(pool, df, table_name):
    load_dotenv()
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
    }
    
    # Create SQLAlchemy engine
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
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
        # Close the database connection
        engine.dispose()



def update_predict_table(pool, final_df):
    load_dotenv()
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
    }
    
    # Create SQLAlchemy engine
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
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

