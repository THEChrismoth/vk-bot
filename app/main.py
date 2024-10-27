from bot import bot
from handlers import labelers

# Подключаем хендлеры
for labeler in labelers:
    bot.labeler.load(labeler)


def start():
    bot.run_forever()


if __name__ == "__main__":
    start()
