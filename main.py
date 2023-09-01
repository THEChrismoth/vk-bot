import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai

# Устанавливаем токен CHATGPT от OpenAI
openai.api_key = 'YOUR_CHATGPT_API_KEY'

# Устанавливаем токен и ID сообщества ВКонтакте
vk_token = 'YOUR_VK_TOKEN'
vk_group_id = 'YOUR_VK_GROUP_ID'

# Инициализируем библиотеку для работы с VK API
vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()

# Функция отправки сообщения
def send_message(user_id, message):
    vk.messages.send(
        peer_id=user_id,
        random_id=vk_api.utils.get_random_id(),
        message=message
    )

# Функция обработки сообщений
def handle_message(event):
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        message = event.text

        # Отправляем сообщение в CHATGPT API и получаем ответ
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=message,
            temperature=0.6,
            max_tokens=50,
            n=1,
            stop=None,
            timeout=5
        )

        # Получаем ответ от CHATGPT
        generated_text = response.choices[0].text.strip()

        # Отправляем ответ пользователю
        send_message(user_id, generated_text)

# Главная функция обработки событий
def main():
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        try:
            handle_message(event)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()