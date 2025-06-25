import psycopg2
from contextlib import contextmanager

@contextmanager
def db_cursor(connection_params):

    conn = psycopg2.connect(**connection_params)
    try:
        cur = conn.cursor()
        yield cur  
        conn.commit()  
    except Exception:
        conn.rollback()  
        raise
    finally:
        cur.close()
        conn.close()
