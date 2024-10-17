from config import labeler
from vkbottle.tools import PhotoMessageUploader
from reader import read_file


photo_uploader = PhotoMessageUploader(bot.api)


@labeler.message(text="начать")
async def start(message):
    photo = await photo_uploader.upload("../images/wolf.png")
    doc = await read_file("../Docs/start.txt")
    await message.answer(doc, attachment=photo)
