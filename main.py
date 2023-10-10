import vk_api
import random
import json
import openai
import random
import sqlite3
import numpy as np

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import group_id, vk_token, openai_api_key

# Устанавливаем токен OpenAI API
openai.api_key = openai_api_key

# Создаем сессию ВКонтакте
vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()

# Создаем подключение к базе данных
conn = sqlite3.connect('chat_history.db')
cursor = conn.cursor()

# Создаем таблицу для хранения переписки
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history
                  (user_id INTEGER, message_text TEXT)''')
conn.commit()

# Функция для отправки сообщения ВКонтакте
def send_message(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(1, 10e9)})

# Функция для сохранения сообщения в базе данных
def save_message(user_id, message_text):
    # Удаляем старые сообщения пользователя, если их количество превышает 3
    cursor.execute(
        f"""
        DELETE FROM chat_history WHERE rowid IN (
            SELECT rowid FROM chat_history WHERE user_id=? ORDER BY rowid LIMIT -1 OFFSET 2
        )
        """,
        (user_id,)
    )

    cursor.execute("INSERT INTO chat_history VALUES (?, ?)", (user_id, message_text))
    conn.commit()
# Функция для получения предыдущих сообщений пользователя из базы данных
def get_previous_messages(user_id):
    cursor.execute("SELECT message_text FROM chat_history WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    previous_messages = []
    for row in rows:
        previous_messages.append({"role": "user", "content": row[0]})
    return previous_messages

# Функция для генерации ответа с использованием OpenAI GPT-3
def generate_response(previous_messages, message_text):
    messages = previous_messages + [{"role": "user", "content": message_text}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Получаем ответ от модели GPT-3.5 Turbo
    reply = response.choices[0].message["content"]

    return reply

# Функция для генерации изображения с помощью OpenAI API
def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']

    return image_url

# Функция для отправки сообщения с изображением в VK
def send_image(user_id, message):
    prompt = message.replace('нарисуй', 'генерировать изображение', 1)  # Замена первого вхождения "нарисуй" на "генерировать изображение"
    image_url = generate_image(prompt)
    vk.messages.send(
        user_id=user_id,
        attachment=image_url,
        message='Ваше сгенерированное изображение',
        random_id=random.randint(1, 1000000)
    )

# Функция для обработки входящих сообщений
def process_message(event):
    user_id = event.obj.message['from_id']
    message_text = event.obj.message['text']

    # Если сообщение начинается с "начать", отправляем приветственное сообщение
    if message_text.lower().startswith("начать"):
        send_message(user_id, "Привет! Я готов помочь тебе. Чем я могу быть полезен?")

    # Если запрос на прошлые сообщения
    elif message_text.lower().startswith("прошлые сообщения"):
        # Получаем предыдущие сообщения пользователя
        previous_messages = get_previous_messages(user_id)

        # Отправляем предыдущие сообщения
        for message in previous_messages:
            send_message(user_id, f"<{message['role']}> {message['content']}")

    #Если просим нарисовать
    elif message_text.lower().startswith("нарисуй"):
        send_image(user_id, message_text)

    # Иначе сохраняем сообщение в базе данных и передаем его модели GPT-3.5 Turbo
    else:
        # Получаем предыдущие сообщения пользователя
        previous_messages = get_previous_messages(user_id)

        # Обрабатываем сообщение и формируем ответ с использованием OpenAI GPT-3
        reply = generate_response(previous_messages, message_text)

        # Сохраняем ответ модели в базе данных
        save_message(user_id, reply)

        max_length = 4000

        if len(reply) > max_length:
            num_messages = len(reply) // max_length + 1

            for i in range(num_messages):
                start_index = i * max_length
                end_index = start_index + max_length
                message = reply[start_index:end_index]
                send_message(user_id, message)
        else:
            send_message(user_id, reply)

# Главная функция обработки событий
def main():
    longpoll = VkBotLongPoll(vk_session, group_id)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            process_message(event)

if __name__ == '__main__':
    main()