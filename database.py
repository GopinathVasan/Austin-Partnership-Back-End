import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector

# Load database configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://user:password@host/db")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASSWORD", "password"),
        database=os.getenv("DB_NAME", "database")
    )

# Create a Base class for declarative_base
Base = declarative_base()
