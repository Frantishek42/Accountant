# import schedule as schedule
from aiogram.utils import executor
from loader import *
from utilit.set_bot_commands import set_default_commands
from logger.log import logger
from database.accountant import *
import handlers


accountant_model = [
    RegisterUser, MergeWithUser, Profit, WalletProfit, Expenses, WalletExpenses, AutoPayment, WalletDB
]


@logger.catch()
async def on_startup(dis: Dispatcher) -> None:
    """
    Функция для запуска функции set_default_commands
    :param dis: Dispatcher
    :return:
    """
    import filters
    # filters.setup(dp)

    await set_default_commands(dis)
    logger.info("Бот запущен!")


if __name__ == '__main__':
    # schedule.every()..at("06:00").do(clear_db)
    for model in accountant_model:
        model.create_table()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
