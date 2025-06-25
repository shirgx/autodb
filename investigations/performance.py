import timeit
import random

from lib import data_gen, backup
from config import db_config
from lib.db import db_cursor
from investigations.plot_utils import plot_results

def measure_data_generation():

    print("--- Измерение производительности генерации данных ---")
    sizes = [100, 1000, 5000, 10000, 50000]
    times = []
    for n in sizes:
        t = timeit.timeit(lambda: data_gen.generate_clients(n), number=1)
        times.append(t)
        print(f"Сгенерировано {n} клиентов за {t:.4f} секунд")

    plot_results(
        x_values=sizes,
        series_dict={"Генерация клиентов": times},
        title="Производительность генерации данных",
        x_label="Количество записей",
        y_label="Время (с)",
        output_file="generation_performance.png"
    )

def measure_insertion_performance():

    print("\n--- Измерение производительности вставки в БД ---")

    def insert_n_clients(n):

        with db_cursor(db_config) as cur:
            cur.execute("TRUNCATE TABLE clients RESTART IDENTITY CASCADE;")
            clients = data_gen.generate_clients(n)
            values = [tuple(item.values()) for item in clients]
            cur.executemany("INSERT INTO clients (name) VALUES (%s);", values)

    sizes = [100, 1000, 5000, 10000]
    times = []
    for n in sizes:
        t = timeit.timeit(lambda: insert_n_clients(n), number=1)
        times.append(t)
        print(f"Вставлено {n} клиентов за {t:.3f}с")

    plot_results(
        x_values=sizes,
        series_dict={"Вставка клиентов (executemany)": times},
        title="Производительность вставки в БД",
        x_label="Количество записей",
        y_label="Время (с)",
        output_file="insertion_performance.png"
    )

def prepare_data_for_joins(n_clients=1000, n_cars=1000, n_orders=5000):

    print("\n--- Подготовка данных для тестов производительности JOIN ---")

    tables_to_truncate = ["order_parts", "order_services", "orders", "cars", "master_profiles", "clients", "masters", "services", "parts"]
    with db_cursor(db_config) as cur:
        for table in tables_to_truncate:

            cur.execute("SELECT to_regclass(%s)", (f'public.{table}',))
            if cur.fetchone()[0]:
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")

    clients = data_gen.generate_clients(n_clients)
    backup.save_data("clients", clients, db_config)

    client_ids = list(range(1, n_clients + 1))
    cars = data_gen.generate_cars(n_cars, client_ids)
    backup.save_data("cars", cars, db_config)

    masters = [{"name": f"Мастер {i}", "specialization": "механик"} for i in range(1, 11)]
    backup.save_data("masters", masters, db_config)

    services = [{"name": f"Услуга {i}", "price": random.randint(50, 500)} for i in range(1, 21)]
    backup.save_data("services", services, db_config)

    car_ids = list(range(1, n_cars + 1))
    master_ids = list(range(1, 11))
    orders = data_gen.generate_orders(n_orders, car_ids, master_ids)
    backup.save_data("orders", orders, db_config)

    print("Данные подготовлены.")

def measure_join_performance():

    print("\n--- Измерение производительности JOIN ---")

    query = """
        SELECT o.order_id, o.order_date, c.name AS client_name, ca.model
        FROM orders o
        JOIN cars ca ON o.car_id = ca.car_id
        JOIN clients c ON ca.client_id = c.client_id
        WHERE o.order_date >= '2025-01-01';
    """

    def run_join_query():
        with db_cursor(db_config) as cur:
            cur.execute(query)
            cur.fetchall()

    run_join_query()

    join_time = timeit.timeit(run_join_query, number=10)
    print(f"JOIN (clients, cars, orders) среднее время: {join_time/10:.4f} с")

def main():

    measure_data_generation()
    measure_insertion_performance()

    prepare_data_for_joins()
    measure_join_performance()

if __name__ == "__main__":
    main()
