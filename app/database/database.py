import psycopg2
from config import DATABASE_URL


# Функция для подключения к базе данных
def connect_to_db():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None
