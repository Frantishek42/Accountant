from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Profit, Number
import keyboards.inline as nav
from states.state_user import FSMUser
from database.profitdb import *
from database.walletdb import WalletDB
from datetime import datetime
from logger.log import logger


async def wallet_money(message: Message) -> None:
    """
    Функция для создания таблицы кошелек и прибавляет сумму денег

    :param message:
    :return:
    """
    WalletDB.create_table()
    money_ = WalletDB.select()
    if money_:
        money_new = 0
        for money in money_:
            money_new = money.money
        money_sum = money_new + int(message.text)
        wall = WalletDB.update(money=money_sum).where(WalletDB.id == 1)
        wall.execute()
        await bot.send_message(message.chat.id, f'Ваш кошелек пополнился на: <b>{message.text}</b> ₱'
                               f'\nДенег в кошелке: <b>{money_sum}</b> ₱')
    else:
        WalletDB.create(id=1, money=message.text)
        await bot.send_message(message.chat.id, f'Ваш кошелек пополнился на: <b>{message.text}</b> ₱')


@dp.message_handler(Profit(), state='*')
async def get_profit(message: Message) -> None:
    logger.info('Зашел добывать прибыль')
    await FSMUser.profit.set()
    await message.answer('Что добавить?', reply_markup=nav.marcup_profit)


@dp.callback_query_handler(state=FSMUser.profit)
async def call_profit(call: CallbackQuery, state: FSMContext) -> None:

    profile_user = {'salary': 'заработной платы', 'part_time_job': 'подработки', 'sale': 'с продажи'}
    logger.info(f'Добавить прибыль: {profile_user.get(call.data)}')
    await FSMUser.user_profit.set()
    async with state.proxy() as data:
        data['profit'] = call.data

    if call.data in profile_user.keys():
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Введите сумму {profile_user.get(call.data)}')


@dp.message_handler(Number(), state=FSMUser.user_profit)
async def profit(message: Message, state: FSMContext) -> None:
    logger.info(f'Сумма к добавлению: {message.text}')
    profit_dict = {'salary': Salary, 'part_time_job': PartTimeJob, 'sale': Sale}
    async with state.proxy() as data:
        profit_user = data.get('profit')
    if profit_user in profit_dict.keys():
        profit_dict.get(profit_user).create_table()
        profit_dict.get(profit_user).create(user_id=message.from_user.id, start_date=datetime.now(), money=message.text)
    await wallet_money(message)
    await state.finish()
