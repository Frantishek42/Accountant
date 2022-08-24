from peewee import OperationalError
from loader import dp
from aiogram.types import Message
from filters.extension_filters import Wallet
from database.walletdb import WalletDB
from logger.log import logger


@dp.message_handler(Wallet(), state='*')
async def get_wallet(message: Message):
    logger.info('Зашел в команду кошелек')
    wallet_user(message)


def wallet_user(message: Message) -> None:
    logger.info('Вывод денег')
    try:
        money = WalletDB.select()
        for i_money in money:
            if 0 < i_money.money < 5000:
                await message.answer(f'В кошелке осталось со всем не много денег: <b>{i_money.money}</b> ₱')
            elif i_money.money < 0:
                await message.answer(f'В кошелке есть задолженность: <b>{i_money.money}</b> ₱')
            else:
                await message.answer(f'В кошелке осталось: <b>{i_money.money}</b> ₱')
    except OperationalError as exc:
        logger.error(exc.__class__.__name__, exc)
        await message.answer('База не создана или удалена')
