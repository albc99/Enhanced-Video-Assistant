from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pyodbc
import json

USERNAME = "tsm-admin"
PASSWORD = "EVAisAwesome!"

SERVER = "evaserverstudent1.database.windows.net"
with open('credentials.json', 'r') as file:
    data = json.load(file)

# Assign values from the JSON file to variables

USERNAME = data['username']
PASSOWRD = data['password']
DATABASE = "evadb"
SERVER = "evaserverstudent1.database.windows.net"

"""
File: database.py
Description: This file contains the functions that interact with the Azure SQL Database.
Functionality: This file is used to connect to the Azure SQL Database.
"""


DATABASE_URL = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver=ODBC Driver 17 for SQL Server"

# Create a synchronous engine instance
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



#use connection pooling..so that it doesnt have to be too expensive to create a new connection each time 
def get_db_connection():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
