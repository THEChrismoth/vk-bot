from config import labeler, admin_id
from bot import bot
from vkbottle import BaseStateGroup, CtxStorage

from functions.gpt_request import gpt_request, gpt_image


# Определяем состояния
class States(BaseStateGroup):
    WAITING_FOR_FORWARD = "waiting_for_forward"
    WAITING_FOR_REQUEST = "waiting_for_request"
    WAITING_FOR_IMAGE = "waiting_for_image"


ctx_storage = CtxStorage()


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


@labeler.message(text="Нарисуй")
async def start_forwarding(message):
    await message.answer("Опишите что вы хотите чтобы я нарисовал")
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FOR_IMAGE)


@labeler.message(state=States.WAITING_FOR_IMAGE)
async def message_to_forward(message):
    answer = await gpt_image(message.text)

    await message.answer(answer.data[0].url)

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)
