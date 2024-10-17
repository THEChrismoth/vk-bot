from vkbottle import API
from vkbottle.bot import BotLabeler

# Устанавливаем токен ВКонтакте API
vk_token = "ваш токен"
api = API(vk_token)
labeler = BotLabeler()

# Указываем идентификатор администратора группы VK
admin_id = "Id_администратора"
