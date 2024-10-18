from config import labeler
from functions.read import read_file


@labeler.message(text="команды")
async def start(message):
    doc = await read_file("comand.txt")
    await message.answer(doc)


@labeler.message(text="начать")
async def start(message):
    image_path = "images/wolf.png"
    await message.answer(attachment=image_path)
