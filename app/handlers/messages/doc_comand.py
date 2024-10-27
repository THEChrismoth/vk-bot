from config import labeler
from functions.read_file import read_file
from functions.mailing import check

labeler.vbml_ignore_case = True


# Хендлер для отправки списка команд по запросу "Команды"
@labeler.message(text="Команды")
async def start(message):
    doc = await read_file("comand.txt")
    await message.answer(doc)


# Хендлер для отправки списка промокодов по запросу "Промокоды"
@labeler.message(text="Промокоды")
async def promo(message):
    doc = await read_file("promo.txt")
    await message.answer(doc)


# Хендлер для отправки списка ивентв по запросу "Иенты"
@labeler.message(text="Ивенты")
async def ivent(message):
    doc = await read_file("ivent.txt")
    await message.answer(doc)


# Хендлер для отправки списка полезных ресурсов от комьюнити по запросу "Полезные ссылки"
@labeler.message(text="Полезные ссылки")
async def resources(message):
    doc = await read_file("resources.txt")
    await message.answer(doc)
