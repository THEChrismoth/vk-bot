from config import labeler, admin_id, GigaChat_authorization
from bot import bot
from vkbottle import BaseStateGroup, CtxStorage

from langchain.schema import HumanMessage
from langchain.chat_models.gigachat import GigaChat


# Определяем состояния
class States(BaseStateGroup):
    WAITING_FOR_FORWARD = "waiting_for_forward"
    WAITING_FOR_REQUEST = "waiting_for_request"


ctx_storage = CtxStorage()

# Авторизация в сервисе
chat = GigaChat(
    credentials=GigaChat_authorization,
    verify_ssl_certs=False,
)


async def generate_response(chat, message_text):
    messages = [HumanMessage(content=message_text)]
    response = chat(messages)
    return response.content


@labeler.message(text="Переслать")
async def start_forwarding(message):
    await message.answer("Напишите сообщение, которое нужно переслать администратору.")
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FOR_FORWARD)


@labeler.message(state=States.WAITING_FOR_FORWARD)
async def message_to_forward(message):
    # Получаем текст сообщения
    remaining_text = "Вам сообщение: " + message.text

    # Отправляем сообщение администратору
    await bot.api.messages.send(user_id=admin_id, message=remaining_text, random_id=0)

    await message.answer("Ваше сообщение отправлено администратору.")

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)


@labeler.message(text="Вульфи")
async def start_forwarding(message):
    await message.answer("Напишите ваш запрос нейросети")
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FOR_REQUEST)


@labeler.message(state=States.WAITING_FOR_REQUEST)
async def message_to_forward(message):
    # Получаем текст сообщения
    remaining_text = message.text
    answer = await generate_response(chat, remaining_text)

    await message.answer(answer)

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)
