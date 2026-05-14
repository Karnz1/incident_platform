import psycopg
from dotenv import load_dotenv
import os
from contextlib import contextmanager

# load environment variables
load_dotenv()

@contextmanager
def get_pg_db():
    conn_info = f'dbname={os.getenv("DATABASE_NAME")} user={os.getenv("USER")} password={os.getenv("PASSWORD")} host={os.getenv("HOST")}'
    conn = psycopg.connect(conn_info)
    try:
        yield conn
    finally:
        print("closing connection")
        conn.close()


