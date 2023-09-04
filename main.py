import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from config import vk_group_id, vk_group_token, openai_api_key

vk_group_id = vk_group_id
vk_group_token = vk_group_token
openai.api_key = openai_api_key

# Функция отправки сообщения
def send_message(user_id, message, attachments=None):
    if attachments:
        vk.messages.send(
            user_id=user_id,
            random_id=vk_api.utils.get_random_id(),
            message=message,
            attachment=attachments
        )
    else:
        vk.messages.send(
            user_id=user_id,
            random_id=vk_api.utils.get_random_id(),
            message=message
        )

# Функция создания клавиатуры
def create_keyboard():
    keyboard = {
        "one_time": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "label": "GPT"
                },
                "color": "positive"
            }],
            [{
                "action": {
                    "type": "text",
                    "label": "Midjourney"
                },
                "color": "positive"
            }]
        ]
    }
    return keyboard

# Функция генерации изображения Midjourney
def generate_midjourney_image(description):
    request_url = "https://api.eleuther.ai/midjourney/vqgan-clip-top-k-sample"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompts": [description],
        "truncation": 0.9,
        "temperature": 0.9,
        "top_k": 0
    }

    response = requests.post(request_url, json=data, headers=headers)
    response_data = response.json()
    image_url = response_data["image"]

    return image_url

# Функция генерации текстового ответа CHATGPT
def generate_chatgpt_response(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0.6,
        max_tokens=50,
        n=1,
        stop=None,
        timeout=5
    )

    return response.choices[0].text.strip()

# Функция обработки сообщений
def handle_message(event):
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        message = event.text

        # Проверяем, является ли пользователь подписчиком сообщества
        is_subscriber = vk.groups.isMember(group_id=vk_group_id, user_id=user_id)

        if not is_subscriber:
            send_message(user_id, "Извините, вы должны быть подписчиком сообщества, чтобы использовать бота.")
            return

        if message.lower() == 'gpt':
            # Отправляем клавиатуру с кнопками GPT
            keyboard = create_keyboard()
            send_message(user_id, "Выберите функционал:", keyboard)
    
        elif message.lower() == 'midjourney':
            # Отправляем клавиатуру с кнопками Midjourney
            keyboard = create_keyboard()
            send_message(user_id, "Выберите функционал:", keyboard)
            
        elif message.lower() == 'привет':
            send_message(user_id, "Привет! Я полезный ассистент. Отправьте команду 'GPT' для работы с GPT или 'Midjourney' для работы с Midjourney.")

        elif message.lower().startswith('midjourney_generate_image:'):
            # Извлекаем описание изображения из сообщения
            description = message.split(':', 1)[1].strip()
            
            # Генерируем изображение Midjourney
            image_url = generate_midjourney_image(description)
            
            # Отправляем изображение пользователю
            response = requests.get(image_url)
            img_data = response.content
            img = BytesIO(img_data)
            plt.imshow(plt.imread(img))
            plt.axis('off')
            plt.show()
            
            send_message(user_id, "Ваше изображение Midjourney:")
            send_message(user_id, "", attachments=img)
            
        else:
            # Отправляем сообщение в CHATGPT API и получаем ответ
            response = generate_chatgpt_response(message)
            
            send_message(user_id, response)

# Инициализация сессии VK API
vk_session = vk_api.VkApi(token=vk_group_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Основной цикл обработки событий
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        handle_message(event)