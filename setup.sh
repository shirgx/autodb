#!/bin/bash
# setup.sh - скрипт для инициализации проекта


echo "Инициализация проекта автосервиса"


echo "Проверяем необходимые пакеты..."
python -c "import psycopg2; import matplotlib; print('Все необходимые пакеты уже установлены')" 2>/dev/null || {
    echo "Установка зависимостей не выполнена. Продолжаем без установки пакетов."
    echo "Если в дальнейшем возникнут ошибки, установите пакеты вручную:"
    echo "python -m pip install psycopg2-binary matplotlib"
}

echo "Проверка PostgreSQL..."

psql -U postgres -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "PostgreSQL доступен с пользователем 'postgres'"
else
    echo "Не удалось подключиться к PostgreSQL с пользователем 'postgres'"
    echo "Пожалуйста, убедитесь, что PostgreSQL установлен и запущен."
    echo "ОШИБКА: PostgreSQL недоступен. Завершение работы."
    exit 1
fi

echo "Проверка наличия базы данных 'autodb'..."
DB_EXISTS=$(psql -U postgres -l | grep autodb | wc -l | tr -d '[:space:]')

if [ "$DB_EXISTS" -eq "0" ]; then
    echo "База данных 'autodb' не найдена. Создаем..."
    createdb -U postgres autodb
    if [ $? -ne 0 ]; then
        echo "ОШИБКА: Не удалось создать базу данных 'autodb'."
        exit 1
    fi
    echo "База данных 'autodb' успешно создана!"
else
    echo "База данных 'autodb' уже существует"
fi

echo "Инициализация структуры базы данных и тестовых данных..."
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"
python -c "
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath('__file__')))

from tests.test_basic import initialize_db, check_db_exists

if check_db_exists():
    initialize_db()
    print('Инициализация выполнена успешно!')
else:
    print('Не удалось подключиться к базе данных. Завершение работы.')
    sys.exit(1)
"

echo "======================"
echo "Инициализация завершена!"
echo "Теперь вы можете запустить тесты производительности:"
echo "cd $SCRIPT_DIR && python -c 'import investigations.performance; investigations.performance.main()'"
echo "cd $SCRIPT_DIR && python -c 'import investigations.index_effectiveness; investigations.index_effectiveness.main()'"
echo "cd $SCRIPT_DIR && python -c 'import investigations.join_performance; investigations.join_performance.main()'"
