import psycopg2

def create_sandbox_db(original_db, sandbox_db, user, password, host="localhost"):

    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host)
    conn.autocommit = True  
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {sandbox_db};")
    cur.execute(f"CREATE DATABASE {sandbox_db} TEMPLATE {original_db};")
    cur.close()
    conn.close()

    