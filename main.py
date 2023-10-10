import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import json
import openai

# Устанавливаем токен OpenAI API
openai.api_key = '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'

# Устанавливаем токен ВКонтакте API
vk_token = 'vk1.a.ebBerU01hNrFYr5kWyBrxtOr5JwBsdSjh5R5pZWTSGnXMXO9ZEOspXBgeeVbRMK2d-AIBKOR_OoPxRGv1yZRcSuQqwf0HY9ymiKdeguaVj9Mrt-rJHqHAuy6iFU1S0vscHRHQ1c1dXbAa7reX3b5XqND71Bu4AfBzTCr_-zMTdUbR4qari80vPaVnXVx_bby6To9CrIvxTThH55VgIvK_w'

# Указываем идентификатор группы VK
group_id = 222543106

# Создаем сессию ВКонтакте
vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()

# Функция для отправки сообщения ВКонтакте
def send_message(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(1, 10e9)})

# Функция для обработки входящих сообщений
def process_message(event):
    user_id = event.obj.message['from_id']
    message_text = event.obj.message['text']

    # Если сообщение начинается с "начать", отправляем приветственное сообщение
    if message_text.lower().startswith("начать"):
        send_message(user_id, "Привет! Я готов помочь тебе. Чем я могу быть полезен?")

    # Иначе, передаем сообщение модели GPT-3.5 Turbo
    else:
        # Передаем сообщение модели GPT-3.5 Turbo в формате чата
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "Вы - пользователь"},
                {"role": "user", "content": message_text}
            ]
        )

        # Получаем ответ от модели GPT-3.5 Turbo
        reply = response.choices[0].message['content']

        # Отправляем ответ пользователю
        send_message(user_id, reply)

# Главная функция обработки событий
def main():
    longpoll = VkBotLongPoll(vk_session, group_id)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            process_message(event)

if __name__ == '__main__':
    main()