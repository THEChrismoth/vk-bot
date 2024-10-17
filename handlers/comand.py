from config import labeler
import os


async def read_file(file_path):
    with open(os.path.join("Docs", file_path), "r", encoding="utf-8") as f:
        return f.read()


@labeler.message(text="команды")
async def start(message):
    doc = await read_file("comand.txt")
    await message.answer(doc)


@labeler.message(text="начать")
async def start(message):
    image_path = "images/wolf.png"
    await message.answer(attachment=image_path)
