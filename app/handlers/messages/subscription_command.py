import psycopg2
from config import labeler
from database.database import connect_to_db

labeler.vbml_ignore_case = True


# Хендлер для добавления ид пользователя в базу данных при команде "Подписаться"
@labeler.message(text="Подписаться")
async def subscribe(message):
    user_id = message.from_id
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        # Проверка на существование таблицы и её создание, если необходимо
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id BIGINT PRIMARY KEY
            )
        """
        )
        connection.commit()

        cursor.execute("INSERT INTO subscribers (user_id) VALUES (%s)", (user_id,))
        connection.commit()
        await message.answer("Вы успешно подписались!")
    except psycopg2.IntegrityError:
        connection.rollback()  # Откат транзакции в случае ошибки
        await message.answer("Вы уже подписаны.")
    except psycopg2.Error as e:
        await message.answer("Произошла ошибка, пожалуйста, попробуйте позже.")
    finally:
        cursor.close()
        connection.close()


# Хендлер для удаления ид пользователя из базы данных при команде "Отписаться"
@labeler.message(text="Отписаться")
async def subscribe(message):
    user_id = message.from_id
    connection = connect_to_db()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM subscribers WHERE user_id = %s", (user_id,))
        connection.commit()

        if cursor.rowcount > 0:
            await message.answer("Вы успешно отписались.")
        else:
            await message.answer("Вы не были подписаны.")
    except psycopg2.Error as e:
        await message.answer("Произошла ошибка, пожалуйста, попробуйте позже.")
    finally:
        cursor.close()
        connection.close()
