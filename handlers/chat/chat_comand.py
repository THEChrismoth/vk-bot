from vkbottle.bot import BotLabeler, Message, rules
from vkbottle_types.objects import MessagesConversation
from functions.read import read_file


class ChatInfoRule(rules.ABCRule[Message]):
    async def check(self, message: Message) -> dict:
        chats_info = await message.ctx_api.messages.get_conversations_by_id(
            message.peer_id
        )
        return {"chat": chats_info.items[0]}


chat_labeler = BotLabeler()
chat_labeler.vbml_ignore_case = True
chat_labeler.auto_rules = [rules.PeerRule(from_chat=True), ChatInfoRule()]


@chat_labeler.message(text="Команды")
async def start(message):
    doc = await read_file("comand.txt")
    await message.answer(doc)


@chat_labeler.message(text="Промокоды")
async def promo(message):
    doc = await read_file("promo.txt")
    await message.answer(doc)


@chat_labeler.message(text="Ивенты")
async def ivent(message):
    doc = await read_file("ivent.txt")
    await message.answer(doc)


@chat_labeler.message(text="Полезные ссылки")
async def resources(message):
    doc = await read_file("resources.txt")
    await message.answer(doc)
