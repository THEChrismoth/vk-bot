import vk_api
import random
import asyncio
import requests
import json
import time
import base64
import numpy as np
import os

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

from config import (
    group_id,
    vk_token,
    GigaChat_authorization,
    admin_id,
    openweathermap_id,
    FB_api_key,
    FB_api_secret_key,
)

# Авторизация в сервисе
chat = GigaChat(
    credentials=GigaChat_authorization,
    verify_ssl_certs=False,
)

# Создаем сессию ВКонтакте
vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()

# Создаем глобальную переменную для блокирование работы
global lock
lock = asyncio.Lock()


# Класс для работы с Fusion Brain Api
class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }

    def get_model(self):
        response = requests.get(
            self.URL + "key/api/v1/models", headers=self.AUTH_HEADERS
        )
        data = response.json()
        return data[0]["id"]

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {"query": f"{prompt}"},
        }

        data = {
            "model_id": (None, model),
            "params": (None, json.dumps(params), "application/json"),
        }
        response = requests.post(
            self.URL + "key/api/v1/text2image/run",
            headers=self.AUTH_HEADERS,
            files=data,
        )
        data = response.json()
        return data["uuid"]

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(
                self.URL + "key/api/v1/text2image/status/" + request_id,
                headers=self.AUTH_HEADERS,
            )
            data = response.json()
            if data["status"] == "DONE":
                return data["images"]

            attempts -= 1
            time.sleep(delay)


# Функция для отправки сообщения ВКонтакте
async def send_message(user_id, message):
    vk.messages.send(
        random_id=random.randint(1, 1000000),
        user_id=user_id,
        message=message,
    )


# Функция для отправки картинки
async def send_picture(user_id, image_path, message):
    upload = vk_api.VkUpload(vk)
    photo = upload.photo_messages(os.path.join("images", image_path))
    vk.messages.send(
        user_id=user_id,
        attachment=f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}',
        message=message,
        random_id=random.randint(1, 1000000),
    )


# Функция поиска имени подписчика
async def get_username(user_id):
    user_info = vk.users.get(user_ids=user_id, fields="screen_name")
    username = (
        f"@{user_info[0]['screen_name']}"
        if "screen_name" in user_info[0]
        else f"Пользователь с id {user_id}"
    )
    return username


# Функция для генерации ответа с использованием GigaChat
async def generate_response(chat, message_text):
    messages = [HumanMessage(content=message_text)]
    response = chat(messages)
    return response.content


# получение погоды
async def get_weather(user_id, city_name):
    # Замените 'your_api_key' на ваш API-ключ OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={openweathermap_id}&units=metric"

    response = requests.get(url)
    data = response.json()

    weather_description = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    response_message = (
        f"Погода в {city_name}: {weather_description}, Температура: {temperature}°C"
    )

    # Отправить сообщение с информацией о погоде пользователю user_id
    await send_message(user_id, response_message)


# функция открытия файла
async def read_file(file_path):
    with open(os.path.join("tx", file_path), "r", encoding="utf-8") as f:
        return f.read()


# Функция для обработки входящих сообщений
async def process_message(event):
    user_id = event.obj.message["from_id"]
    message_text = event.obj.message["text"]

    if message_text.lower() == "начать" or message_text.lower().startswith("привет"):
        message = await read_file("start.txt")
        await send_picture(user_id, "wolf.png", message)

    elif message_text.lower().startswith("команды") or message_text.lower().startswith(
        "что ты умеешь"
    ):
        message = await read_file("comand.txt")
        await send_message(user_id, message)

    elif message_text.lower().startswith("промокоды"):
        message = await read_file("promo.txt")
        await send_message(user_id, message)

    elif message_text.lower().startswith("ивенты"):
        message = await read_file("ivent.txt")
        await send_message(user_id, message)

    elif message_text.lower().startswith("полезные ссылки"):
        message = await read_file("resources.txt")
        await send_message(user_id, message)

    elif message_text.lower().startswith("переслать"):
        user_name = await get_username(user_id)
        message = f"Сообщение от подписчика {user_name}: {message_text[9:]}"
        await send_message(admin_id, message)

    elif message_text.lower().startswith("погода"):
        worlds = message_text.split()
        city_name = " ".join(worlds[1:])
        await get_weather(user_id, city_name)

    elif message_text.lower().startswith("нарисуй"):
        worlds = message_text.split()
        message_image = " ".join(worlds[1:])
        async with lock:
            api = Text2ImageAPI(
                "https://api-key.fusionbrain.ai/",
                FB_api_key,
                FB_api_secret_key,
            )
            model_id = api.get_model()
            uuid = api.generate(message_image, model_id)
            images = api.check_generation(uuid)
            image_base64 = images[0]
            image_data = base64.b64decode(image_base64)
            with open(os.path.join("images", "image.jpg"), "wb") as file:
                file.write(image_data)
            message = "Ваше изображение"
            await send_picture(user_id, "image.jpg", message)

    elif message_text.lower().startswith("вульфи"):
        Chad_join = message_text.split()
        Chad_message = " ".join(Chad_join[1:])
        async with lock:
            reply = await generate_response(chat, Chad_message)
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
