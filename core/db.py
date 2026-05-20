import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

connection_pool = pool.SimpleConnectionPool(
    minconn=2,
    maxconn=10,
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

def close_all_connections():
    connection_pool.closeall()