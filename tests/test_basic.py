import sys
from lib import schema, data_gen, backup
from lib.db import db_cursor
from config import db_config
import psycopg2
from psycopg2 import sql

def check_db_exists():
    try:

        conn = psycopg2.connect(**db_config)
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print(f"База данных '{db_config['dbname']}' не существует!")
            print("Пожалуйста, создайте базу данных с помощью команды:")
            print(f"createdb {db_config['dbname']}")
            return False
        elif "password authentication failed" in str(e):
            print("Ошибка аутентификации в PostgreSQL.")
            print("Проверьте правильность имени пользователя и пароля в config.py.")
            return False
        else:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            return False

def initialize_db():

    print("Создание таблиц...")
    schema.create_tables(db_config)

    print("Генерация тестовых данных...")
    clients = data_gen.generate_clients(5)
    inserted = backup.save_data("clients", clients, db_config)
    print(f"Добавлено {inserted} клиентов")

    cars = data_gen.generate_cars(3, client_ids=list(range(1, 6)))
    car_count = backup.save_data("cars", cars, db_config)
    print(f"Добавлено {car_count} автомобилей")

    with db_cursor(db_config) as cur:
        cur.execute("SELECT COUNT(*) FROM cars WHERE client_id = %s;", (1,))
        count = cur.fetchone()[0]
        print(f"Автомобилей у клиента с id=1: {count}")

if __name__ == "__main__":
    print("Инициализация базы данных автосервиса...")

    if not check_db_exists():
        print("Не удалось подключиться к базе данных. Завершение работы.")
        sys.exit(1)

    initialize_db()
    print("Инициализация завершена успешно!")
