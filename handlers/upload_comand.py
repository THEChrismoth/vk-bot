from config import labeler
from bot import bot
from vkbottle import PhotoMessageUploader
from functions.read import read_file

photo_uploader = PhotoMessageUploader(bot.api)


@labeler.message(text="Начать")
async def Photo_upload(message):
    doc = await read_file("start.txt")
    photo = await photo_uploader.upload(
        file_source="images/wolf.png",
        peer_id=message.peer_id,
    )
    await message.answer(doc, attachment=photo)
