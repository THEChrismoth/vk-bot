from config import labeler
from functions.read import read_file


@labeler.message(text="Команды")
async def start(message):
    doc = await read_file("comand.txt")
    await message.answer(doc)


@labeler.message(text="Промокоды")
async def promo(message):
    doc = await read_file("promo.txt")
    await message.answer(doc)


@labeler.message(text="Ивенты")
async def ivent(message):
    doc = await read_file("ivent.txt")
    await message.answer(doc)


@labeler.message(text="Полезные ссылки")
async def resources(message):
    doc = await read_file("resources.txt")
    await message.answer(doc)
