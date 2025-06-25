import timeit
import random
from datetime import datetime, timedelta

from lib import data_gen, backup
from config import db_config
from lib.db import db_cursor
from investigations.plot_utils import plot_results

def prepare_data(n_clients=1000, n_cars=2000, n_orders=5000):

    print("Подготовка данных для тестов JOIN...")

    clients = data_gen.generate_clients(n_clients)
    backup.save_data("clients", clients, db_config)

    client_ids = list(range(1, n_clients + 1))
    cars = data_gen.generate_cars(n_cars, client_ids)
    backup.save_data("cars", cars, db_config)

    masters = [
        {"name": f"Мастер {i}", "specialization": random.choice(["Механик", "Электрик", "Маляр", "Диагност"])}
        for i in range(1, 21)
    ]
    backup.save_data("masters", masters, db_config)

    car_ids = list(range(1, n_cars + 1))
    master_ids = list(range(1, 21))
    orders = data_gen.generate_orders(n_orders, car_ids, master_ids)
    backup.save_data("orders", orders, db_config)

    print(f"Готово! Создано {n_clients} клиентов, {n_cars} автомобилей, 20 мастеров, {n_orders} заказов.")

def test_simple_join():

    query_simple = """
    SELECT c.name, ca.model, ca.year
    FROM clients c
    JOIN cars ca ON c.client_id = ca.client_id
    LIMIT 1000;
    """

    def run_query():
        with db_cursor(db_config) as cur:
            cur.execute(query_simple)
            return cur.fetchall()

    run_query()

    time_taken = timeit.timeit(run_query, number=10)
    print(f"Простой JOIN (clients, cars) среднее время: {time_taken/10:.4f} с")
    return time_taken/10

def test_complex_join():

    query_complex = """
    SELECT c.name, ca.model, o.order_date
    FROM clients c
    JOIN cars ca ON c.client_id = ca.client_id
    JOIN orders o ON ca.car_id = o.car_id
    WHERE o.order_date >= '2025-01-01'
    LIMIT 1000;
    """

    def run_query():
        with db_cursor(db_config) as cur:
            cur.execute(query_complex)
            return cur.fetchall()

    run_query()

    time_taken = timeit.timeit(run_query, number=10)
    print(f"Сложный JOIN (clients, cars, orders с условием) среднее время: {time_taken/10:.4f} с")
    return time_taken/10

def main():

    with db_cursor(db_config) as cur:
        cur.execute("SELECT COUNT(*) FROM clients;")
        client_count = cur.fetchone()[0]

    if client_count < 1000:
        prepare_data()

    print("\n--- Тестирование производительности JOIN-запросов ---")
    simple_join_time = test_simple_join()
    complex_join_time = test_complex_join()

    plot_results(
        x_values=["Простой JOIN", "Сложный JOIN"],
        series_dict={"Среднее время выполнения (с)": [simple_join_time, complex_join_time]},
        title="Сравнение производительности различных JOIN-запросов",
        x_label="Тип запроса",
        y_label="Время выполнения (с)",
        output_file="join_performance_comparison.png"
    )

if __name__ == "__main__":
    main()
