import mysql.connector

# Database configuration
db_config = {
    'host': '82.180.142.240',
    'user': 'u490928194_APD',
    'password': 'APD@apd123',
    'database': 'u490928194_APD'
}

# Function to establish database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)
