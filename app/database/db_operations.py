import os
import psycopg2
from icecream import ic

from config import DB_CONFIG

# Path to the SQL queries
QUERY_PATH = 'app/database/queries/'

def get_query(query_name):
    """Fetch SQL from a file."""
    with open(os.path.join(QUERY_PATH, f"{query_name}.sql"), 'r') as file:
        return file.read()

def execute_query(query_name, params=None):
    """Execute a query using its name and optional parameters."""
    sql = get_query(query_name)
    
    try:
        # Connect to the PostgreSQL server
        connection = psycopg2.connect(**DB_CONFIG)
        

        # Create a new cursor
        cursor = connection.cursor()
        
        # Execute the SQL command
        cursor.execute(sql, params)
        
        # If the SQL command is a SELECT statement, fetch the results. NOTE: SQL is case insensitive so use .lower method.
        if "select" in sql.lower():
            result = cursor.fetchall()
        else:
            result = None
        
        # Commit the changes, if any
        connection.commit()
        
        # Close the connection
        cursor.close()
        connection.close()

        return result

    except psycopg2.DatabaseError as error:
        print(f"Error: {error}")
        return None

# Additional database utility functions can be added here.
