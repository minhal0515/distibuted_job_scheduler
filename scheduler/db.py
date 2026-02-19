import psycopg

def get_conn():
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="scheduler_db",
        user="scheduler",
        password="scheduler",
        autocommit=False,
        connect_timeout=5,
    )
