# import schedule as schedule
from aiogram.types import Message
from aiogram.utils import executor
from filters import UserID
from loader import *
from utilit.set_bot_commands import set_default_commands
import keyboards.reply as nav
from logger.log import logger


@logger.catch()
async def on_startup(dis: Dispatcher) -> None:
    """
    Функция для запуска функции set_default_commands
    :param dis: Dispatcher
    :return:
    """
    import filters
    await filters.setup(dp)

    await set_default_commands(dis)
    logger.info("Бот запущен!")


@logger.catch()
@dp.message_handler(UserID(), commands=['start'], state='*')
async def process_start_command(message: Message) -> None:
    """
    Функция для запуска бота
    :param message:
    :return:
    """
    import handlers
    await message.reply(f"Добро пожаловать {message.from_user.first_name}!", reply_markup=nav.marcup)


if __name__ == '__main__':
    # schedule.every()..at("06:00").do(clear_db)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
