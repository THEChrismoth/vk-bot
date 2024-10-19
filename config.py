from vkbottle import API
from vkbottle.bot import BotLabeler

# Устанавливаем токен ВКонтакте API
vk_token = "токен вк"
api = API(vk_token)
labeler = BotLabeler()

# Указываем идентификатор администратора группы VK
admin_id = "ваш ид"

# Указываем авторизационные данные OpenAI
GPT_key = "ключ гпт"
