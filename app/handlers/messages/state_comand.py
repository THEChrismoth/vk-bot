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

labeler.vbml_ignore_case = True


# Хендлер для создания состояния ожидания сообщения для пересылки
@labeler.message(text="Переслать")
async def start_forwarding(message):
    await message.answer("Напишите сообщение, которое нужно переслать администратору.")
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FOR_FORWARD)


# Хендлер для отправки сообщения от пользователя в состоянии ожидания сообщения
@labeler.message(state=States.WAITING_FOR_FORWARD)
async def message_to_forward(message):
    user = await bot.api.users.get(message.from_id)
    # Получаем текст сообщения
    remaining_text = "Вам сообщение :" + message.text

    # Отправляем сообщение администратору
    await bot.api.messages.send(user_id=admin_id, message=remaining_text, random_id=0)

    await message.answer("Ваше сообщение отправлено администратору.")

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)


# Хендлер для создания состояния ожидания запроса к нейросети
@labeler.message(text="Включить")
async def start_forwarding(message):
    await message.answer("Напишите ваш запрос нейросети")
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FOR_REQUEST)


# Хендлер для отправки ответа нейросети пользователю состояния ожидания запроса
@labeler.message(state=States.WAITING_FOR_REQUEST)
async def message_to_forward(message):
    if message.text == "Выключить":
        # Возвращаем пользователя в начальное состояние
        await bot.state_dispenser.delete(message.peer_id)

        await message.answer("Вы вышли из режима нейросети")
    else:
        answer = await gpt_request(message.text)

        await message.answer(answer.choices[0].message.content)


# Хендлер для создания состояния ожидания запроса для рисовки изображения
@labeler.message(text="Нарисуй")
async def start_forwarding(message):
    await message.answer("Опишите что вы хотите чтобы я нарисовал")
    await bot.state_dispenser.set(message.peer_id, States.WAITING_FOR_IMAGE)


# Хендлер для отправки изображения полученного нейросетью
@labeler.message(state=States.WAITING_FOR_IMAGE)
async def message_to_forward(message):
    answer = await gpt_image(message.text)

    await message.answer(answer.data[0].url)

    # Возвращаем пользователя в начальное состояние
    await bot.state_dispenser.delete(message.peer_id)
