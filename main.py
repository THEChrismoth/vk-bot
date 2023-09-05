import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import requests

# Ваш Access Token
VK_TOKEN= "vk1.a.LWZ4oNx1PFVmjGqWEal83WHLEioPVUppDY0zNDqR23HBVqFqhHtiKpI78HWn-d-EahZsXhGacqc5IUnJSGDbVXLFm5Dtjnz1L-cT54XT-d_qqUMjUCK7uJClVHE3D6VAwindWj7ot-0ZsHfEo8e0ejacKVbRAH7k3WdKOVpCCnqY-kTddDGr_rAv7gTQNiPux2ACk5SS64jWrSPnF2dZ0A"
# Ваш API-ключ ChatGPT
CHATGPT_API_KEY = "your_chatgpt_api_key"
# Ваш API-ключ Midjourney
MIDJOURNEY_API_KEY = "your_midjourney_api_key"


# Подключение к API ВКонтакте
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Список подписчиков рассылки
subscribers = []

# Функция для отправки запроса к ChatGPT
def chat_gpt_request(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": message,
        "max_tokens": 50
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()["choices"][0]["text"]

# Функция для отправки запроса к Midjourney
def midjourney_request(message):
    url = "https://api.midjourney.com/conversation"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MIDJOURNEY_API_KEY}"
    }
    data = {
        "messages": [message]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()["response"]

# Функция для отправки рассылки
def send_newsletter(message):
    for subscriber in subscribers:
        vk.messages.send(user_id=subscriber, message=message, random_id=random.getrandbits(31))

# Создание клавиатуры
def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Подписаться на рассылку", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отписаться от рооссылки", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("ChatGPT", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Midjourney", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Написать админу", color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()

# Функция для обработки рассылки
def handle_newsletter(message):
    if message.startswith("рассылка:"):
        newsletter_text = message.replace("рассылка:", "").strip()
        send_newsletter(newsletter_text)
        vk.messages.send(user_id=user_id, message="Рассылка отправлена!", random_id=random.getrandbits(31), keyboard=create_keyboard())
    else:
        vk.messages.send(user_id=user_id, message="Некорректная команда для рассылки!", random_id=random.getrandbits(31), keyboard=create_keyboard())


# Функция для отправки изображений
def send_image(user_id, image_url):
    upload_url = vk.photos.getMessagesUploadServer()["upload_url"]
    response = requests.post(upload_url, files={"photo": open(image_url, "rb")})
    result = response.json()
    photo_data = vk.photos.saveMessagesPhoto(photo=result["photo"], server=result["server"], hash=result["hash"])[0]
    attachments = f"photo{photo_data['owner_id']}_{photo_data['id']}"
    vk.messages.send(user_id=user_id, message="Привет! Я полезный ассистент. Чем могу помочь?", attachment=attachments, random_id=random.getrandbits(31), keyboard=create_keyboard())

# Основной код бота
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        message = event.text.lower()
        user_id = event.user_id
        
        # Проверка команды для клавиатуры
        if message == "подписаться":
            if user_id not in subscribers:
                subscribers.append(user_id)
                vk.messages.send(user_id=user_id, message="Вы подписались на рассылку!", random_id=random.getrandbits(31), keyboard=create_keyboard())
            else:
                vk.messages.send(user_id=user_id, message="Вы уже подписаны на рассылку!", random_id=random.getrandbits(31), keyboard=create_keyboard())
        
        elif message == "отписаться":
            if user_id in subscribers:
                subscribers.remove(user_id)
                vk.messages.send(user_id=user_id, message="Вы отписались от рассылки!", random_id=random.getrandbits(31), keyboard=create_keyboard())
            else:
                vk.messages.send(user_id=user_id, message="Вы не подписаны на рассылку!", random_id=random.getrandbits(31), keyboard=create_keyboard())
        
        elif message == "начать":
            introduction_image_url = "C:\photoshop\ENORS3ws1cs.jpg"  # Замените на URL нужной вам картинки
            send_image(user_id, introduction_image_url)
            
        elif message == "chatgpt":
            vk.messages.send(user_id=user_id, message="Какой вопрос у вас есть?", random_id=random.getrandbits(31), keyboard=create_keyboard())
        
        elif message == "midjourney":
            vk.messages.send(user_id=user_id, message="Что вы хотите сгенерировать?", random_id=random.getrandbits(31), keyboard=create_keyboard())
        
        elif message == "написать админу":
            vk.messages.send(user_id=user_id, message="Напишите ваше сообщение администратору.", random_id=random.getrandbits(31))
        
        elif message.startswith("рассылка:") and user_id == ADMIN_USER_ID:
            handle_newsletter(message)
        
        elif user_id in subscribers:
            # Отправка запроса к ChatGPT
            if message.startswith("chatgpt:"):
                question = message.replace("chatgpt:", "").strip()
                chatgpt_response = chat_gpt_request(question)
                vk.messages.send(user_id=user_id, message=chatgpt_response, random_id=random.getrandbits(31), keyboard=create_keyboard())
            
            # Отправка запроса к Midjourney
            elif message.startswith("midjourney:"):
                request = message.replace("midjourney:", "").strip()
                midjourney_response = midjourney_request(request)
                vk.messages.send(user_id=user_id, message=midjourney_response, random_id=random.getrandbits(31), keyboard=create_keyboard())
            
            else:
                # Отправка сообщения об ошибке, если пользователь ввел некорректную команду
                vk.messages.send(user_id=user_id, message="Некорректная команда!", random_id=random.getrandbits(31), keyboard=create_keyboard())
        
        else:
            # Отправка сообщения об ошибке, если пользователь не подписан на рассылку
            vk.messages.send(user_id=user_id, message="Вы не подписаны на рассылку!", random_id=random.getrandbits(31), keyboard=create_keyboard())