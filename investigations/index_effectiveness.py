import timeit
import random

from config import db_config
from lib.db import db_cursor
from investigations.plot_utils import plot_results
from lib import data_gen, backup, schema

def prepare_base_data(max_size):

    print(f"--- Проверка и подготовка данных (требуется {max_size} заказов) ---")

    schema.create_tables(db_config)

    with db_cursor(db_config) as cur:

        cur.execute("SELECT COUNT(*) FROM orders;")
        count = cur.fetchone()[0]
        if count >= max_size:
            print("В таблице orders уже достаточно данных.")
            return

        print(f"В таблице 'orders' {count} записей. Требуется сгенерировать еще {max_size - count}.")

        cur.execute("SELECT COUNT(*) FROM clients;")
        if cur.fetchone()[0] < 100:
            clients = data_gen.generate_clients(100)
            backup.save_data("clients", clients, db_config)

        cur.execute("SELECT client_id FROM clients;")
        client_ids = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT COUNT(*) FROM cars;")
        if cur.fetchone()[0] < 200:
            cars_data = data_gen.generate_cars(200, client_ids=client_ids)
            backup.save_data("cars", cars_data, db_config)

        cur.execute("SELECT car_id FROM cars;")
        car_ids = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT COUNT(*) FROM masters;")
        if cur.fetchone()[0] < 20:
            masters = [{"name": f"Мастер {i}", "specialization": "механик"} for i in range(1, 21)]
            backup.save_data("masters", masters, db_config)

        cur.execute("SELECT master_id FROM masters;")
        master_ids = [r[0] for r in cur.fetchall()]

        orders_to_gen = max_size - count
        orders = data_gen.generate_orders(orders_to_gen, car_ids, master_ids)
        backup.save_data("orders", orders, db_config)
        print(f"{orders_to_gen} заказов успешно сгенерировано и добавлено.")

def measure_select_performance(sizes):

    print("\n--- Измерение влияния индекса на SELECT ---")
    times_indexed = []
    times_no_index = []

    with db_cursor(db_config) as cur:
        for n in sizes:
            print(f"\nТестирование на {n} записях...")
            t_indexed = f"temp_indexed_{n}"
            t_no_index = f"temp_no_index_{n}"

            cur.execute(f"DROP TABLE IF EXISTS {t_indexed}, {t_no_index};")

            cur.execute(f"CREATE TABLE {t_no_index} AS SELECT * FROM orders ORDER BY order_id LIMIT {n};")

            cur.execute(f"CREATE TABLE {t_indexed} AS TABLE {t_no_index};")
            cur.execute(f"ALTER TABLE {t_indexed} ADD PRIMARY KEY (order_id);")

            cur.execute(f"ANALYZE {t_indexed};")
            cur.execute(f"ANALYZE {t_no_index};")

            cur.execute(f"SELECT order_id FROM {t_no_index} ORDER BY random() LIMIT 100;")
            keys_to_find = [row[0] for row in cur.fetchall()]
            if not keys_to_find:
                print("Не удалось выбрать ключи для поиска. Пропуск.")
                times_indexed.append(0)
                times_no_index.append(0)
                continue

            def search_indexed():
                for key in keys_to_find:
                    cur.execute(f"SELECT * FROM {t_indexed} WHERE order_id = %s;", (key,))
                    cur.fetchone()

            def search_no_index():
                for key in keys_to_find:
                    cur.execute(f"SELECT * FROM {t_no_index} WHERE order_id = %s;", (key,))
                    cur.fetchone()

            search_indexed()
            search_no_index()

            t_indexed_time = timeit.timeit(search_indexed, number=10)
            t_no_index_time = timeit.timeit(search_no_index, number=10)

            avg_indexed = t_indexed_time / (10 * len(keys_to_find))
            avg_no_index = t_no_index_time / (10 * len(keys_to_find))

            times_indexed.append(avg_indexed)
            times_no_index.append(avg_no_index)
            print(f"  Среднее время поиска с индексом: {avg_indexed:.8f} с")
            print(f"  Среднее время поиска без индекса: {avg_no_index:.8f} с")

            cur.execute(f"DROP TABLE {t_indexed}, {t_no_index};")

    plot_results(
        x_values=sizes,
        series_dict={
            "SELECT с индексом (PK)": times_indexed,
            "SELECT без индекса": times_no_index
        },
        title="Влияние индекса на скорость SELECT по ключу",
        x_label="Количество записей в таблице",
        y_label="Среднее время на один SELECT (с)",
        output_file="select_index_vs_noindex.png"
    )

def main():

    test_sizes = [1000, 5000, 10000, 20000, 50000]
    prepare_base_data(max(test_sizes))
    measure_select_performance(test_sizes)

if __name__ == "__main__":
    main()

