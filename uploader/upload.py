from vkbottle import PhotoMessageUploader
from main import bot

photo_uploader = PhotoMessageUploader(bot.api)


@bot.on.message(text="photo")
async def Photo_upload(message):
    photo = await photo_uploader.upload(
        file_source="images/wolf.png",
        peer_id=message.peer_id,
    )
    await message.answer(attachment=photo)
