import asyncio
import aioschedule
from aiogram.utils import executor
from loader import *
from utilit.set_bot_commands import set_default_commands
from logger.log import logger
from database.accountant import *
import handlers
from peewee import OperationalError, DoesNotExist
import time
import datetime


accountant_model = [
    RegisterUser, UserSubscription, MergeWithUser, Profit, WalletProfit, Expenses, WalletExpenses, AutoPayment, WalletDB
]


async def get_user_private():
    try:
        private = UserSubscription.select().where(UserSubscription.time_sub <= time.time())
        for time_sub in private:
            user_id = RegisterUser.get(RegisterUser.id == time_sub.user_id)
            dt = datetime.timedelta(seconds=int(time_sub.time_sub) - int(time.time()))
            if dt.days < 10:
                dt = str(dt).replace('days', 'дней')
                dt = dt.replace('day', 'день')
                await bot.send_message(user_id.user_id, f'Подписка скоро закончится через {dt}')
            elif dt.days == 0:
                await bot.send_message(user_id.user_id, 'Подписка отключена')
    except DoesNotExist as exc:
        logger.info(f'В таблице нет ни одной записи {exc.__class__.__name__}')
    except OperationalError as exc:
        logger.error(f"{exc.__class__.__name__} {exc}")


async def scheduler():

    aioschedule.every().day.at("15:42").do(get_user_private)
    logger.info('Запушена проверка подписки')
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def restart():
    """
    Функция для отправки сообщения пользователем после перезапуска бота

    :return:
    """
    try:
        users = RegisterUser.select()
        for user in users:
            await bot.send_message(user.user_id, 'Сообщаем вам что бот запушен.\nДля запуска нажмите /start')

    except DoesNotExist as exc:
        logger.info(f'Таблица пользователей пуста {exc.__class__.__name__}')
    except OperationalError as exc:
        logger.error(f'{exc.__class__.__name__}')


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
    asyncio.create_task(scheduler())
    await restart()


if __name__ == '__main__':

    for model in accountant_model:
        model.create_table()

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
