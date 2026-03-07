import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="mars_postgres",
        database="mars_habitat",
        user="zazaki",
        password="hackathon2026",
        port="5432",
        cursor_factory=RealDictCursor
    )