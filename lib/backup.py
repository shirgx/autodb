from lib.db import db_cursor

def save_data(table_name, data, conn_params):

    if not data:
        return 0

    columns = list(data[0].keys())
    cols_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

    values = [tuple(item[col] for col in columns) for item in data]
    with db_cursor(conn_params) as cur:
        cur.executemany(query, values)
    return len(data)

def clear_table(table_name, conn_params):

    with db_cursor(conn_params) as cur:
        cur.execute(f"DELETE FROM {table_name};")

import csv

def backup_database(conn_params, backup_dir="./backup"):
    tables = ["clients", "masters", "master_profiles", "cars",
              "services", "parts", "orders", "order_services", "order_parts"]
    with db_cursor(conn_params) as cur:
        for table in tables:
            cur.execute(f"SELECT * FROM {table};")
            rows = cur.fetchall()

            with open(f"{backup_dir}/{table}.csv", "w", newline="") as f:
                writer = csv.writer(f)

                col_names = [desc[0] for desc in cur.description]
                writer.writerow(col_names)

                writer.writerows(rows)

def restore_database(conn_params, backup_dir="./backup"):
    tables = ["clients", "masters", "master_profiles", "cars",
              "services", "parts", "orders", "order_services", "order_parts"]
    with db_cursor(conn_params) as cur:
        for table in tables:
            with open(f"{backup_dir}/{table}.csv", "r") as f:
                reader = csv.reader(f)
                columns = next(reader)  

                cols_str = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(columns))
                insert_query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
                for row in reader:
                    cur.execute(insert_query, row)