from peewee import OperationalError
from loader import dp
from aiogram.types import Message
from filters.extension_filters import WalletFilter
from database.walletdb import WalletDB
from logger.log import logger


@dp.message_handler(WalletFilter(), state='*')
async def get_wallet(message: Message):
    """
    Функция для приема команды Кошелек
    :param message: Message
    :return:
    """
    logger.info('Зашел в команду кошелек')
    await wallet_user(message)


async def wallet_user(message: Message) -> None:
    """
    Функция для вывода информации кошелька
    :param message:
    :return:
    """
    logger.info('Вывод денег')
    try:
        money = WalletDB.select().where(WalletDB.id == 1).get()

        money_sum = money.money_card + money.money_cash - money.money_credit
        if 0 < money_sum < 5000:
            await message.answer(f'В кошелке осталось со всем не много денег:'
                                 f'\nНа карте: <b>{money.money_card}</b> ₱'
                                 f'\nНаличных: <b>{money.money_cash}</b> ₱'
                                 f'\nЗадолженность по кредитке: <b>{money.money_credit}</b> ₱'
                                 f'\nОбщая сумма: <b>{money_sum}</b> ₱'
                                 )
        elif money_sum < 0:
            await message.answer(f'В кошелке есть задолженность: '
                                 f'\nНа карте: <b>{money.money_card}</b> ₱'
                                 f'\nНаличных: <b>{money.money_cash}</b> ₱'
                                 f'\nЗадолженность по кредитке: <b>{money.money_credit}</b> ₱'
                                 f'\nОбщая сумма: <b>{money_sum}</b> ₱'
                                 )
        else:
            await message.answer(f'В кошелке осталось: '
                                 f'\nНа карте: <b>{money.money_card}</b> ₱'
                                 f'\nНаличных: <b>{money.money_cash}</b> ₱'
                                 f'\nЗадолженность по кредитке: <b>{money.money_credit}</b> ₱'
                                 f'\nОбщая сумма: <b>{money_sum}</b> ₱'
                                 )
    except OperationalError as exc:
        logger.error(exc.__class__.__name__, exc)
        await message.answer('База не создана или удалена')
