from config import vk_token
from handlers import labelers

import os

from vkbottle.bot import Message, Bot
from vkbottle import PhotoMessageUploader

bot = Bot(vk_token)
photo_uploader = PhotoMessageUploader(bot.api)


async def read_file(file_path):
    with open(os.path.join("Docs", file_path), "r", encoding="utf-8") as f:
        return f.read()


@bot.on.message(text="photo")
async def Photo_upload(message):
    photo = await photo_uploader.upload(
        file_source="images/wolf.png",
        peer_id=message.peer_id,
    )
    doc = await read_file("start.txt")
    await message.answer(doc, attachment=photo)


for labeler in labelers:
    bot.labeler.load(labeler)

bot.run_forever()
