from lib.db import db_cursor
from config import db_config

def create_tables(conn_params):

    create_sql = [
        """
        CREATE TABLE IF NOT EXISTS clients (
            client_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS masters (
            master_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialization VARCHAR(50) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS master_profiles (
            master_id INTEGER PRIMARY KEY REFERENCES masters(master_id) ON DELETE CASCADE,
            bio TEXT,
            experience INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS cars (
            car_id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE,
            model VARCHAR(50) NOT NULL,
            year INTEGER NOT NULL CHECK (year > 1900)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS services (
            service_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price NUMERIC(10,2) NOT NULL CHECK (price > 0)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS parts (
            part_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price NUMERIC(10,2) NOT NULL CHECK (price > 0)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            car_id INTEGER REFERENCES cars(car_id) ON DELETE RESTRICT,
            master_id INTEGER REFERENCES masters(master_id) ON DELETE RESTRICT,
            order_date DATE NOT NULL DEFAULT CURRENT_DATE,
            total_cost NUMERIC(10,2) DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_services (
            order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
            service_id INTEGER REFERENCES services(service_id) ON DELETE RESTRICT,
            quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            PRIMARY KEY (order_id, service_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_parts (
            order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
            part_id INTEGER REFERENCES parts(part_id) ON DELETE RESTRICT,
            quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            PRIMARY KEY (order_id, part_id)
        )
        """
    ]
    with db_cursor(conn_params) as cur:
        for sql in create_sql:
            cur.execute(sql)