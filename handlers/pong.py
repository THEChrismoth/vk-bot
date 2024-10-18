from config import labeler, api
from bot import bot
from vkbottle import PhotoMessageUploader

photo_uploader = PhotoMessageUploader(bot.api)


@labeler.message(text="photo")
async def Photo_upload(message):
    photo = await photo_uploader.upload(
        file_source="images/wolf.png",
        peer_id=message.peer_id,
    )
    await message.answer(attachment=photo)
