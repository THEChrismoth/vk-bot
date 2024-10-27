import datetime
from database.database import connect_to_db
from bot import bot, lw


# Функция для отправки сообщения всем подписчикам
async def send_weekly_message(message):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM subscribers")
    subscribers = cursor.fetchall()

    for subscriber in subscribers:
        user_id = subscriber[0]
        await bot.api.messages.send(user_id=user_id, message=message, random_id=0)

    cursor.close()
    connection.close()


# Функция для проверки даты и времени + задачи для рассылки
async def check():
    # Получение текущего времени
    current_time = datetime.datetime.now().strftime("%H:%M")
    # Получение текущего дня недели (0 - понедельник, 6 - воскресенье)
    current_weekday = datetime.datetime.now().weekday()

    # Ивент Битва династий в понедельник
    Monday_BD = "20:10"
    BD_MESSAGE = "Начинается Битва династий"
    # Ивент Битва за ледник во вторник
    Tuesday_BZD = "19:50"
    BZD_MESSAGE = "Начинается Битва за ледник"
    # Ивент Танцы в кх в среду
    Wednesday_KH = "19:20"
    KH_MESSAGE = "Заходим на кх на танцы"
    # Ивент Адепты в среду
    Wednesday_ADEPT = "19:50"
    ADEPT_MESSAGE = "Собираемся на Адептов"
    # Ивент кр в четверг
    Thursday_KR = "19:30"
    KR_MESSAGE = "Сбор на КР"
    # Ивент Битва династий в пятницу
    Friday_BD = "20:10"
    # Ивент МТВ в субботу
    Saturday_MTV = "19:30"
    MTV_MESSAGE = "Сбор на МТВ"
    # Ивент Дракон Садеман в Субботу
    Saturday_SADEMAN = "21:30"
    SADEMAN_MESSAGE = "Сбор на Дракона Садемана"

    # Проверяем, совпадает ли текущее время с заданным
    if current_time == Monday_BD and current_weekday == 0:
        await send_weekly_message(BD_MESSAGE)
    elif current_time == Tuesday_BZD and current_weekday == 1:
        await send_weekly_message(BZD_MESSAGE)
    elif current_time == Wednesday_KH and current_weekday == 2:
        await send_weekly_message(KH_MESSAGE)
    elif current_time == Wednesday_ADEPT and current_weekday == 2:
        await send_weekly_message(ADEPT_MESSAGE)
    elif current_time == Thursday_KR and current_weekday == 3:
        await send_weekly_message(KR_MESSAGE)
    elif current_time == Friday_BD and current_weekday == 4:
        await send_weekly_message(BD_MESSAGE)
    elif current_time == Saturday_MTV and current_weekday == 5:
        await send_weekly_message(MTV_MESSAGE)
    elif current_time == Saturday_SADEMAN and current_weekday == 5:
        await send_weekly_message(SADEMAN_MESSAGE)


# Проверяем дату и время каждые 45 секунд
@lw.interval(seconds=45)
async def work_check():
    await check()
