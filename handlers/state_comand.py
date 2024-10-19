from config import labeler, admin_id, GPT_key
from bot import bot
from vkbottle import BaseStateGroup, CtxStorage

from httpx import AsyncClient

from openai import AsyncOpenAI


# Определяем состояния
class States(BaseStateGroup):
    WAITING_FOR_FORWARD = "waiting_for_forward"
    WAITING_FOR_REQUEST = "waiting_for_request"


ctx_storage = CtxStorage()


# Создаем экземпляр клиента OpenAI с использованием прокси и базы данных
gpt = AsyncOpenAI(
    api_key=GPT_key,
    base_url="https://api.proxyapi.ru/openai/v1",
    http_client=AsyncClient(),
)


# Функция для получения ответов от модели GPT
async def gpt_request(text):
    response = await gpt.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": str(text)}]
    )
    return response


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
    answer = await gpt_request(message.text)

    await message.answer(answer.choices[0].message.content)

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)
