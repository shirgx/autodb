import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_basic import initialize_db, check_db_exists

if __name__ == "__main__":
    print("Инициализация базы данных автосервиса...")

    if not check_db_exists():
        print("Не удалось подключиться к базе данных. Завершение работы.")
        sys.exit(1)

    initialize_db()
    print("Инициализация завершена успешно!")
