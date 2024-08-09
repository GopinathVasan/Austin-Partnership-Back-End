from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector

# Define the database URL with the correct format
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://u490928194_APD:APD%40apd123@82.180.142.240/u490928194_APD"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_connection():
    return mysql.connector.connect(
        host='82.180.142.240',
        user='u490928194_APD',
        password='APD@apd123',
        database='u490928194_APD'
    )


# def get_db_connection():
#     return mysql.connector.connect(**SQLALCHEMY_DATABASE_URL)

# Create a Base class for declarative_base
Base = declarative_base()








# import mysql.connector

# # Database configuration
# db_config = {
#     'host': '82.180.142.240',
#     'user': 'u490928194_APD',
#     'password': 'APD@apd123',
#     'database': 'u490928194_APD'
# }

# # Function to establish database connection
# def get_db_connection():
#     try:
#         connection = mysql.connector.connect(**db_config)
#         return connection
#     except mysql.connector.Error as e:
#         print(f"Error connecting to MySQL database: {e}")
#         raise

# # Function to close database connection
# def close_db_connection(connection):
#     if connection:
#         connection.close()
