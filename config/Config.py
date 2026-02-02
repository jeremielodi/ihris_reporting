from config.Database import  dbParams
from dotenv import load_dotenv
import os
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