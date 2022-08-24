from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Expenses, Number
import keyboards.inline as nav
from states.state_user import FSMUser
from database.expensesdb import *
from database.walletdb import WalletDB
from datetime import datetime
from logger.log import logger


@dp.message_handler(Expenses(), state='*')
async def get_expenses(message: Message):
    """
    Функция для отлавливания команды затраты
    :param message: Message
    :return:
    """
    await FSMUser.expenses.set()
    await message.answer('Что добавить?', reply_markup=nav.marcup_expenses)


@dp.callback_query_handler(state=FSMUser.expenses)
async def call_expenses(call: CallbackQuery, state: FSMContext) -> None:

    expenses_user = {'products': 'продукты', 'alcohol': 'алкоголь', 'chemistry': 'химию', 'communal': 'ЖКХ',
                     'credit': 'кредит', 'gas_station': 'АЗС', 'car': 'машину', 'online_store': 'интернет магазине',
                     'other': 'прочие'}
    logger.info(f'Затраты на {expenses_user.get(call.data)}')
    answer = call.data
    async with state.proxy() as data:
        data['expenses'] = answer
    if call.data == 'other':
        await FSMUser.expenses_other.set()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Прочие затраты:', reply_markup=nav.marcup_other)
        return
    prefix = 'на'
    if call.data in expenses_user.keys():
        await FSMUser.user_expenses.set()
        if call.data == 'online_store':
            prefix = 'в'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Введите сколько потратили {prefix} {expenses_user.get(call.data)}')


@dp.callback_query_handler(state=FSMUser.expenses_other)
async def other(call: CallbackQuery, state: FSMContext) -> None:
    expenses_other = {'clothes': 'Одежду', 'connection': 'Связь', 'rest': 'Отдых', 'eyes': 'Глаза',
                      'materials': 'Материалы', 'internet': 'Интернет, ТВ', 'gifts': 'Подарки', 'animals': 'Животных',
                      'the_others': 'Другие'}
    logger.info(f'Затраты на {expenses_other.get(call.data)}')
    if call.data == 'back':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Что добавить?', reply_markup=nav.marcup_expenses)
        await FSMUser.expenses.set()
        return

    if call.data in expenses_other.keys():
        async with state.proxy() as data:
            data['expenses_other'] = expenses_other.get(call.data)
        await FSMUser.user_expenses.set()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Введите сколько потратили на {expenses_other.get(call.data)}')


@dp.message_handler(Number(), state=FSMUser.user_expenses)
async def user_expenses(message: Message, state: FSMContext) -> None:

    logger.info(f'Денег потрачено: {message.text}')
    async with state.proxy() as data:
        expenses = data.get('expenses')
        name = data.get('expenses_other')

    expenses_user = {'products': Products, 'alcohol': Alcohol, 'chemistry': Chemistry, 'communal': Communal,
                     'credit': Credit, 'gas_station': GasStation, 'car': Car, 'online_store': OnlineStore}
    if expenses == 'other':
        Other.create_table()
        Other.create(user_id=message.from_user.id, start_date=datetime.now(), money=message.text, name=name)
    else:
        if expenses in expenses_user.keys():
            expenses_user.get(expenses).create_table()
            expenses_user.get(expenses).create(user_id=message.from_user.id, start_date=datetime.now(),
                                               money=message.text)
    await wallet_money(message)
    await state.finish()


async def wallet_money(message: Message) -> None:
    """
    Функция для создания таблицы кошелек и

    :param message:
    :return:
    """
    try:
        cash = WalletDB.select()
        if cash:
            money = 0
            for i_money in cash:
                money = i_money.money
            if money > int(message.text):
                money_new = money - int(message.text)
                wall = WalletDB.update(money=money_new).where(WalletDB.id == 1)
                wall.execute()
                await bot.send_message(message.chat.id, f'Ваш кошелек похудел на <b>{message.text}</b>'
                                                        f'\nДенег в кошелке осталось: <b>{money_new}</b> ₱')
            else:
                money_new = money - int(message.text)
                wall = WalletDB.update(money=money_new).where(WalletDB.id == 1)
                wall.execute()
                await message.answer(f'Вы зашли за лимит. Задолженность составляет: <b>{money_new}</b>')
        else:
            WalletDB.create(id=1, money=message.text)
    except OperationalError as exp:
        logger.error(exp.__class__.__name__, exp)
        await message.answer('База данных кошелек не создана или удалена')
