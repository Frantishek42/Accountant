from asyncio import sleep
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Number
import keyboards.inline as nav
from states.state_user import FSMUser
from database.accountant import Profit, WalletProfit, WalletDB, RegisterUser
from peewee import DoesNotExist, OperationalError
from logger.log import logger
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Button

profile_user = {'salary': 'заработная плата', 'part_time_job': 'подработка', 'gift': 'подарок', 'sale': 'продажа'}


@logger.catch()
async def profit(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для приема команды Прибыль
    :param button:
    :param dialog_manager:
    :param call:
    :return:
    """
    print(call.data)
    logger.info(f'Пользователь {call.from_user.first_name} зашел добывать прибыль')
    await dialog_manager.start(FSMUser.profit, mode=StartMode.RESET_STACK)


async def call_profit(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для отлавливания кнопок прибыль
    :param dialog_manager:
    :param button:
    :param call:
    :return:
    """
    logger.info(f'Добавить прибыль: {profile_user.get(call.data)}')
    await FSMUser.profit_money.set()
    async with dialog_manager.data.get('state').proxy() as data:
        data['profit'] = profile_user.get(call.data)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Вы выбрали {profile_user.get(call.data)}')
    if call.data in profile_user.keys():
        await call.message.answer('Теперь выберите вид зачисление', reply_markup=nav.marcup_money)


@dp.callback_query_handler(state=FSMUser.profit_money)
async def call_profit_money(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager) -> None:
    """
    Функция для отлавливания кнопок marcup_money
    :param dialog_manager:
    :param call:
    :param state:
    :return:
    """
    profile_money = {'card': 'карту', 'cash': 'наличные', 'card_cash': 'нал безнал'}

    if call.data in 'back':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вернутся в меню прибыли')
        await dialog_manager.start(FSMUser.profit, mode=StartMode.NEW_STACK)
        await state.finish()
        return
    profit_ = profile_money.get(call.data)
    logger.info(f'Пополнить: {profit_}')
    await FSMUser.user_profit.set()
    async with state.proxy() as data:
        data['profit_money'] = call.data
    if call.data in profile_money.keys():
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Пополнить {profit_}')


@dp.message_handler(Number(), state=FSMUser.user_profit)
@logger.catch()
async def get_profit(message: Message, dialog_manager: DialogManager, state: FSMContext) -> None:
    """
    Функция для создании таблицы (Profit, WalletProfit)  и добавления в нее информации
    :param dialog_manager:
    :param message:
    :param state:
    :return:
    """
    logger.info(f'Сумма к добавлению: {message.text}')

    user_id = RegisterUser.get(RegisterUser.user_id == message.from_user.id)

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

    profit_ = None
    try:
        profit_, created = Profit.get_or_create(name=profit_user)
    except OperationalError as exc:
        logger.error(f'{exc.__class__.__name__}, {exc}')
    WalletProfit.create_table()
    WalletProfit.create(user_id=user_id.id, profit_name=profit_, money_card=card, money_cash=cash)
    await wallet_money(message, dialog_manager, state)
    await state.finish()


async def wallet_money(message: Message, dialog_manager: DialogManager, state: FSMContext) -> None:
    """
    Функция для создания таблицы кошелек и прибавляет сумму денег

    :param dialog_manager:
    :param state:
    :param message:
    :return:
    """
    user_id = RegisterUser.get(RegisterUser.user_id == message.from_user.id)
    async with state.proxy() as data:
        profit_money = data.get('profit_money')

    money_new_card = 0
    money_new_cash = 0
    if profit_money == 'card':
        money_new_card = int(message.text)
    elif profit_money == 'cash':
        money_new_cash = int(message.text)
    else:
        money_new_card = int(message.text.split()[1])
        money_new_cash = int(message.text.split()[0])
    money_profit = money_new_card + money_new_cash

    try:
        money = WalletDB.select().where(WalletDB.id == 1).get()
        money_new_card += money.money_card
        money_new_cash += money.money_cash

        wall = WalletDB.update(
            money_card=money_new_card, money_cash=money_new_cash
        ).where(WalletDB.user_id == user_id.id)
        wall.execute()

    except DoesNotExist as exc:
        logger.info(f'{exc.__class__.__name__}, {exc}')
        WalletDB.create(user_id=user_id.id, money_card=money_new_card, money_cash=money_new_cash)
    except OperationalError as exc:
        logger.error(f'{exc.__class__.__name__} {exc}')
    with open('media/gif/money.gif', 'rb') as file:
        file_id = await bot.send_animation(chat_id=message.chat.id, animation=file, duration=None,
                                           caption=f'Ваш баланс пополнился на: <b>{money_profit}</b> ₱')
    await sleep(3)
    await bot.delete_message(chat_id=message.chat.id, message_id=file_id.message_id)
    await dialog_manager.start(FSMUser.profit, mode=StartMode.NEW_STACK)

