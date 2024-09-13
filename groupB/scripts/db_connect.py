import numpy as np
import pandas as pd
import pymysql
import mysql.connector

endpoint = 'my-rds-instance.123456789012.us-east-1.rds.amazonaws.com'
username = 'admin'
password = 'mypassword'
database = 'mydatabase'

# Set the database credentials
host = '<YOUR_RDS_ENDPOINT>'
port = 3306
user = '<YOUR_DATABASE_USERNAME>'
password = '<YOUR_DATABASE_PASSWORD>'
database = '<YOUR_DATABASE_NAME>'

# Connect to the database
connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

# Create a cursor object
cursor = connection.cursor()

# Execute a SQL query
cursor.execute('SELECT * FROM environment')

# Fetch the results
results = cursor.fetchall()

# Print the results
for result in results:
    print(result)

# Close the cursor and connection
cursor.close()
connection.close()

