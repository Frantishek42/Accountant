from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import ProfitFilter, Number
import keyboards.inline as nav
from states.state_user import FSMUser
from database.profitdb import *
from database.walletdb import WalletDB
from logger.log import logger

profile_user = {'salary': 'заработная платы', 'part_time_job': 'подработка', 'sale': 'продажа'}


async def wallet_money(message: Message, state: FSMContext) -> None:
    """
    Функция для создания таблицы кошелек и прибавляет сумму денег

    :param state:
    :param message:
    :return:
    """
    async with state.proxy() as data:
        profit_money = data.get('profit_money')

    money_new_card = 0
    money_new_cash = 0
    money_credit = 0
    if profit_money == 'card':
        money_new_card = int(message.text)
    elif profit_money == 'cash':
        money_new_cash = int(message.text)
    else:
        money_new_card = int(message.text.split()[1])
        money_new_cash = int(message.text.split()[0])
    money_profit = money_new_card + money_new_cash

    WalletDB.create_table()
    try:
        money = WalletDB.select().where(WalletDB.id == 1).get()
        money_new_card += money.money_card
        money_new_cash += money.money_cash
        money_credit = money.money_credit

        wall = WalletDB.update(money_card=money_new_card, money_cash=money_new_cash).where(WalletDB.id == 1)
        wall.execute()

    except DoesNotExist as exc:
        logger.info(f'{exc.__class__.__name__}, {exc}')
        WalletDB.create(money_card=money_new_card, money_cash=money_new_cash)
    money_sum = money_new_card + money_new_cash
    await bot.send_message(message.chat.id, f'Ваш баланс пополнился на: <b>{money_profit}</b> ₱'
                                            f'\nБаланс:'
                                            f'\nНа карте:  <b>{money_new_card}</b> ₱'
                                            f'\nНаличные: <b>{money_new_cash}</b> ₱'
                                            f'\nЗадолженность по кредитке: <b>{money_credit}</b> ₱'
                                            f'\nОбщая сумма: <b>{money_sum - money_credit}</b> ₱')


@dp.message_handler(ProfitFilter(), state='*')
async def get_profit(message: Message) -> None:
    """
    Функция для приема команды Прибыль
    :param message:
    :return:
    """
    logger.info('Зашел добывать прибыль')
    await FSMUser.profit.set()
    await message.answer('Что добавить?', reply_markup=nav.marcup_profit)


@dp.callback_query_handler(state=FSMUser.profit)
async def call_profit(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для отлавливания кнопок marcup_profit
    :param call:
    :param state:
    :return:
    """
    logger.info(f'Добавить прибыль: {profile_user.get(call.data)}')
    await FSMUser.profit_money.set()
    async with state.proxy() as data:
        data['profit'] = call.data
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Вы выбрали {profile_user.get(call.data)}')
    if call.data in profile_user.keys():
        await call.message.answer('Теперь выберите категорию', reply_markup=nav.marcup_money)


@dp.callback_query_handler(state=FSMUser.profit_money)
async def call_profit_money(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для отлавливания кнопок marcup_money
    :param call:
    :param state:
    :return:
    """
    profile_money = {'card': 'карту', 'cash': 'наличные', 'card_cash': 'нал безнал'}
    profit = profile_money.get(call.data)
    logger.info(f'Пополнить: {profit}')
    await FSMUser.user_profit.set()
    async with state.proxy() as data:
        data['profit_money'] = call.data

    if call.data in profile_money.keys():
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Пополнить {profit}')


@dp.message_handler(Number(), state=FSMUser.user_profit)
@logger.catch()
async def get_profit(message: Message, state: FSMContext) -> None:
    """
    Функция для создании таблицы (Profit, WalletProfit)  и добавления в нее информации
    :param message:
    :param state:
    :return:
    """
    logger.info(f'Сумма к добавлению: {message.text}')

    async with state.proxy() as data:
        profit_user = data.get('profit')
        profit_money = data.get('profit_money')

    card = 0
    cash = 0
    if profit_money in 'card':
        card = message.text
    elif profit_money in 'cash':
        cash = message.text
    elif profit_money in 'card_cash' and len(message.text.split()) == 2:
        card = message.text.split()[1]
        cash = message.text.split()[0]
    else:
        await message.answer('Данные ведены неверно. Попробуйте еще раз.\nВведите через пробел нал безнал')
        return

    Profit.create_table()
    profit = None
    try:
        profit = Profit.select().where(Profit.name == profile_user.get(profit_user)).get()
    except DoesNotExist as exc:
        logger.info(f'{exc.__class__.__name__}, {exc}')
        profit = Profit.create(name=profile_user.get(profit_user)).select(). \
            where(Profit.name == profile_user.get(profit_user)).get()
    except OperationalError as exc:
        logger.error(f'{exc.__class__.__name__}, {exc}')
    WalletProfit.create_table()
    WalletProfit.create(user_id=message.from_user.id, profit_name=profit, money_card=card, money_cash=cash)
    await wallet_money(message, state)
    await state.finish()
