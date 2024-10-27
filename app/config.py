from vkbottle import API
from vkbottle.bot import BotLabeler
import os

# Устанавливаем токен ВКонтакте API
vk_token = "Ваш токен вконтакте"
api = API(vk_token)
labeler = BotLabeler()

# Указываем идентификатор администратора группы VK
admin_id = "Ваш ид как администратора"

# Указываем авторизационные данные OpenAI
GPT_key = "Ваш токен для OpenAI"

DATABASE_URL = os.getenv("DATABASE_URL", "default_value_if_not_set")
