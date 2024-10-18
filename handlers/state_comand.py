from config import labeler, admin_id, GigaChat_authorization
from bot import bot
from vkbottle import BaseStateGroup, CtxStorage

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

import aiohttp
import asyncio
from aiohttp import ClientSession


# Определяем состояния
class States(BaseStateGroup):
    WAITING_FOR_FORWARD = "waiting_for_forward"
    WAITING_FOR_REQUEST = "waiting_for_request"


ctx_storage = CtxStorage()


async def generate_response(message_text):
    async with ClientSession() as session:

        async def get_response():
            async with session.post(
                "https://api.gigachat.ai/v2/chats",
                json={"credentials": GigaChat_authorization, "verify_ssl_certs": False},
                data={"messages": [{"content": message_text}]},
            ) as resp:
                if resp.status == 200:
                    return await resp.json()

        response = await get_response()
        return response["content"]


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
    answer = await generate_response(message.text)

    await message.answer(answer)

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)
