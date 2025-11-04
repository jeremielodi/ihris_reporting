
import mysql.connector
from config.Database import  dbParams
from dotenv import load_dotenv
import os

def mysql_get_mydb():

    '''Returns a connection to   MYSQL.'''
    try:
        cnx = mysql.connector.connect(
            host=  dbParams['host'],
            user = dbParams['user'],
            passwd = dbParams['passwd'],
            database = dbParams['database'])
    
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == mysql.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

        cnx.reconnect()

    return  cnx

import psycopg2
from psycopg2 import OperationalError, errors
from config.Database import dbParams

def pg_get_mydb():
    """Returns a connection to PostgreSQL."""

    try:
        load_dotenv()
        
        conn = psycopg2.connect(
            host= os.getenv("DB_HOST"),
            user= os.getenv("DB_USER"),
            password=  os.getenv("DB_PASSWORD"),   # psycopg2 uses "password" not "passwd"
            dbname= os.getenv("DB_NAME"),
            port=  os.getenv("DB_PORT")  # default to 5432
        )
        return conn

    except OperationalError as err:
        # psycopg2 doesn’t have the same errorcode constants as MySQL
        print(f"Database connection error: {err}")
        return None