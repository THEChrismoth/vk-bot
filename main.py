import vk_api
import random
import json
import openai
import random
import sqlite3
import asyncio
import requests
import numpy as np

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import group_id, vk_token, openai_api_key, admin_id, openweathermap_id

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
async def send_message(user_id, message):
   vk.messages.send(
        random_id=random.randint(1, 1000000),
        user_id=user_id,
        message=message,
    )

# Функция для сохранения сообщения в базе данных
async def save_message(user_id, message_text):
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

#получение погоды
async def get_weather(user_id, city_name):   
    # Замените 'your_api_key' на ваш API-ключ OpenWeatherMap
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={openweathermap_id}&units=metric'

    response = requests.get(url)
    data = response.json()

    weather_description = data['weather'][0]['description']
    temperature = data['main']['temp']
    response_message = f"Погода в {city_name}: {weather_description}, Температура: {temperature}°C"

    # Отправить сообщение с информацией о погоде пользователю user_id
    await send_message(user_id, response_message)

    
# Функция для получения предыдущих сообщений пользователя из базы данных
async def get_previous_messages(user_id):
    cursor.execute("SELECT message_text FROM chat_history WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    previous_messages = []
    for row in rows:
        previous_messages.append({"role": "user", "content": row[0]})
    return previous_messages

# Функция для генерации ответа с использованием OpenAI GPT-3
async def generate_response(previous_messages, message_text):
    messages = previous_messages + [{"role": "user", "content": message_text}]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Получаем ответ от модели GPT-3.5 Turbo
    reply = response.choices[0].message.content

    return reply    

# Функция для генерации изображения с помощью OpenAI API
async def generate_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        quality="standard",
        size="1024x1024"
    )
    image_url = response.data[0].url

    return image_url

# Функция для отправки сообщения с изображением в VK
async def send_image(user_id, message):
    prompt = message.replace('нарисуй', 'генерировать изображение', 1)  # Замена первого вхождения "нарисуй" на "генерировать изображение"
    image_url = await generate_image(prompt)
    vk.messages.send(
        user_id=user_id,
        attachment=image_url,
        message='Ваше сгенерированное изображение',
        random_id=random.randint(1, 1000000)
    )

# Функция для отправки картинки
async def send_picture(user_id, image_path):
    upload = vk_api.VkUpload(vk)
    photo = upload.photo_messages(image_path)
    vk.messages.send(
        user_id=user_id,
        attachment= f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}',
        message='Твое приветственное сообщение',
        random_id=random.randint(1, 1000000)
    )

#Функция поиска имени подписчика
async def get_username(user_id):
    user_info = vk.users.get(user_ids=user_id, fields='screen_name')
    username = f"@{user_info[0]['screen_name']}" if 'screen_name' in user_info[0] else f"Пользователь с id {user_id}"
    return username

# Функция для обработки входящих сообщений
async def process_message(event):
    user_id = event.obj.message['from_id']
    message_text = event.obj.message['text']

    # Если сообщение начинается с "начать", отправляем приветственное сообщение
    if message_text.lower().startswith("начать") or message_text.lower().startswith("кто ты") :
        await send_picture(user_id, 'изображение.png')

    elif message_text.lower().startswith('команды') or message_text.lower().startswith("что ты умеешь") :
        vk.messages.send(
            random_id=random.randint(1, 1000000),
            user_id=user_id,
            message='Вот что я умею:\n\n-Начать - стартовое сообщение\n-Команды - список команд\n-Погода (название города) - прогноз погоды\n-Переслать (ваше сообщение) - переслать сообщение администратору\n-Нарисуй (ваша идея на английском) - генерация изображений\n\nВсе остальные сообщени распозноются как ChatGPt\n\nРад буду помочь)',
        )   

    elif message_text.lower().startswith('погода'):
        words = message_text.split()
        city_name = ' '.join(words[1:])  # Получаем все слова после "погода" как название города
        await get_weather(user_id, city_name)

    elif message_text.lower().startswith('переслать'):
        user_name = await get_username(user_id)
        message = f"Сообщение от подписчика {user_name}: {message_text[9:]}"  # Заменяем "Переслать" на "Сообщение от подписчика"
        await send_message(admin_id, message)
        
    # Если запрос на прошлые сообщения
    elif message_text.lower().startswith("прошлые сообщения"):
        # Получаем предыдущие сообщения пользователя
        previous_messages = await get_previous_messages(user_id)

        # Отправляем предыдущие сообщения
        for message in previous_messages:
            await send_message(user_id, f"<{message['role']}> {message['content']}")

    #Если просим нарисовать
    elif message_text.lower().startswith("нарисуй"):
        await send_image(user_id, message_text)

    # Иначе сохраняем сообщение в базе данных и передаем его модели GPT-3.5 Turbo
    else:
        # Получаем предыдущие сообщения пользователя
        previous_messages = await get_previous_messages(user_id)

        # Обрабатываем сообщение и формируем ответ с использованием OpenAI GPT-3
        reply = await generate_response(previous_messages, message_text)

        # Сохраняем ответ модели в базе данных
        await save_message(user_id, reply)

        max_length = 4000

        if len(reply) > max_length:
            num_messages = len(reply) // max_length + 1

            for i in range(num_messages):
                start_index = i * max_length
                end_index = start_index + max_length
                message = reply[start_index:end_index]
                await send_message(user_id, message)
        else:
            await send_message(user_id, reply)

# Главная функция обработки событий
async def main():  
    longpoll = VkBotLongPoll(vk_session, group_id)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
           await process_message(event)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())