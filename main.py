from vkbottle import Bot
from config import api
from handlers import labelers

bot = Bot(api=api)

for labeler in labelers:
    bot.labeler.load(labeler)

bot.run_forever()
