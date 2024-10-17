from vkbottle import Bot
from handlers import labeler
from config import api, labeler

bot = Bot(
    api=api,
    labeler=labeler,
)

bot.run_forever()
