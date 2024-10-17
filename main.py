from vkbottle import Bot
from .handlers import labelers

for labeler in labelers:
    bot.labeler.load(labeler)

bot.run_forever()
