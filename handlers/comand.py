from config import labeler, admin_id
from reader import read_file
from main import bot

from vkbottle.tools import PhotoMessageUploader
from vkbottle.bot import Message

photo_uploader = PhotoMessageUploader(bot.api)


@labeler.message(text="начать")
async def start(message: Message):
    photo = await photo_uploader.upload("../images/wolf.png")
    doc = await read_file("../Docs/start.txt")
    await message.answer(doc, attachment=photo)


@labeler.message(text="команды")
async def start(message: Message):
    doc = await read_file("../Docs/comand.txt")
    await message.answer(doc)


@labeler.message(text="промокоды")
async def start(message: Message):
    doc = await read_file("../Docs/promo.txt")
    await message.answer(doc)


@labeler.message(text="полезные ссылки")
async def start(message: Message):
    doc = await read_file("../Docs/resources.txt")
    await message.answer(doc)


@labeler.message(text="переслать")
async def start(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    message = f"Сообщение от подписчика {users_info[0].first_name}: {Message.text[9:]}"
    await bot.api.messages.send(peer_id=admin_id, message=message, random_id=0)
