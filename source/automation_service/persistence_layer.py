import psycopg2
from psycopg2.extras import RealDictCursor
import os

# "mars_db" è il nome del servizio nel tuo docker-compose
DB_HOST = os.getenv("DB_HOST", "mars_db") 

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database="mars_habitat",
        user="zazaki",
        password="hackathon2026",
        port="5432",
        cursor_factory=RealDictCursor
    )
