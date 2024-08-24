import pandas as pd
from database import get_db_connection
# from database import get_db_connection  # Import your custom DB connection

# Read Excel file
excel_file_path = r'C:\Users\vasan\OneDrive\Documents\data.csv'
# df = pd.read_excel(excel_file_path)
df = pd.read_csv(excel_file_path)

# Convert the DataFrame to a list of tuples (assuming the table has the same columns as the DataFrame)
data = [tuple(row) for row in df.to_numpy()]

# Define the table and SQL query
table_name = 'AP_LLP_DETAILS_DAY_TRADE_PROFITS'
sql_query = f"INSERT INTO {table_name} (col1, col2, col3, ...) VALUES (%s, %s, %s, ...)"  # Update column names

try:
    # Use the connection from your DB connection module
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Insert data into the table
    cursor.executemany(sql_query, data)
    connection.commit()
    
    print(f"Inserted {cursor.rowcount} rows into the database.")

except Exception as e:
    print(f"Error: {e}")
    
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("Database connection closed.")
