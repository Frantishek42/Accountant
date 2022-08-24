from loader import dp
from aiogram.types import Message


@dp.message_handler(commands=['help'])
async def process_help_command(message: Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")
