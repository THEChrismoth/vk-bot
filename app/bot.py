from vkbottle.bot import Message, Bot
from config import api, labeler
from vkbottle import LoopWrapper

lw = LoopWrapper()
bot = Bot(api=api, labeler=labeler, loop_wrapper=lw)
