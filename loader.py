from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from config_data.config import BOT_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)
