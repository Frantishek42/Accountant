from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Number
import keyboards.inline as nav
from keyboards.inline import marcup_expenses_user
from keyboards.inline import marcup_auto_payment
from states.state_user import FSMUser
from database.accountant import Expenses, WalletDB, WalletExpenses, RegisterUser
from peewee import *
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from logger.log import logger

expenses_user = {
    'products': 'продукты', 'alcohol': 'алкоголь', 'communal': 'ЖКХ', 'gas_station': 'АЗС', 'car': 'машину',
    'online_store': 'интернет магазин', 'clothes': 'Одежда', 'connection': 'Связь', 'rest': 'Отдых',
    'add_choose': 'Добавить / выбрать свое'
}
payment = {'card': 'картой', 'cash': 'наличными', 'card_cash': 'нал. безнал'}


async def get_expenses(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для приема команды Затраты
    :param dialog_manager:
    :param button:
    :param call:
    :return:
    """
    logger.info(f'Пользователь {call.from_user.first_name} зашли в команду Затраты')
    # await dialog_manager.dialog().switch_to(FSMUser.expenses)
    await dialog_manager.start(FSMUser.expenses, mode=StartMode.RESET_STACK)


async def call_expenses(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция отлавливает кнопки marcup_expenses
    :param dialog_manager:
    :param button:
    :param call:
    :return:
    """
    logger.info(f'Затраты на {expenses_user.get(call.data)}')
    answer = call.data
    async with dialog_manager.data.get('state').proxy() as data:
        data['expenses'] = expenses_user.get(answer)
    if call.data == 'add_choose':
        marcup = marcup_expenses_user(call.message)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Выберите из списка или добавить новую.', reply_markup=marcup)
        await FSMUser.other.set()

        return

    await FSMUser.expenses_money.set()
    prefix = 'На'
    if call.data == 'online_store':
        prefix = 'В'
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'{prefix} {expenses_user.get(call.data)}')
    await call.message.answer('Выберите вид оплаты:', reply_markup=nav.marcup_money)
    async with dialog_manager.data.get('state').proxy() as data:
        data['expenses_add'] = expenses_user.get(call.data)


@dp.callback_query_handler(state=FSMUser.other)
async def get_add(call: CallbackQuery, dialog_manager: DialogManager) -> None:

    if call.data == 'add':
        logger.info(f'Пользователь {call.from_user.first_name} добавляет затрату')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Введите название затраты')
        await FSMUser.expenses_add.set()
        return
    elif call.data == 'back':
        logger.info(f'Пользователь {call.from_user.first_name} вернулся в меню затрат')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вернуться в меню затрат')
        await dialog_manager.start(FSMUser.expenses, mode=StartMode.NEW_STACK)
        await dialog_manager.data.get('state').finish()
        return

    elif call.data.split(' ')[0].isalpha():
        logger.info(f'Пользователь {call.from_user.first_name} выбрал затрату {expenses_user.get(call.data)}')
        async with dialog_manager.data.get('state').proxy() as data:
            data['expenses_add'] = call.data
        await FSMUser.expenses_money.set()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Затрата: {call.data}')
        await call.message.answer('Выберите вид оплаты', reply_markup=nav.marcup_money)
    elif call.data.split(':')[0] == 'prev':
        logger.info(f'Пользователь {call.from_user.first_name} листает список своих затрат назад')
        if int(call.data.split(':')[1]) > 0:
            prev = int(call.data.split(':')[1]) - 1
            next_ = prev + 1
            marcup = marcup_expenses_user(call.message, prev=prev, next_=next_)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Выберите из списка или добавить новую.', reply_markup=marcup)
    elif call.data.split(':')[0] == 'next':
        logger.info(f'Пользователь {call.from_user.first_name} листает список своих затрат вперед')
        if int(call.data.split(':')[1]) < int(call.data.split(':')[2]):
            next_ = int(call.data.split(':')[1]) + 1
            prev = next_ - 1
            marcup = marcup_expenses_user(call.message, prev=prev, next_=next_)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Выберите из списка или добавить новую.', reply_markup=marcup)





@dp.message_handler(state=FSMUser.expenses_add)
async def other(message: Message, state: FSMContext) -> None:
    """
    Функция отлавливает кнопки marcup_other
    :param message:
    :param state:
    :return:
    """
    logger.info(f'Затраты на {message.text}')

    async with state.proxy() as data:
        data['expenses_add'] = message.text
    await FSMUser.expenses_money.set()
    await message.answer(f'Затрата: {message.text}')
    await message.answer('Выберите вид оплаты', reply_markup=nav.marcup_money)


@dp.callback_query_handler(state=FSMUser.expenses_money)
async def expenses_money(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager) -> None:
    """
    Функция отлавливает кнопки marcup_money
    :param dialog_manager:
    :param call:
    :param state:
    :return:
    """
    logger.info(f'Выберите вид оплаты: {payment.get(call.data)}')
    if call.data in 'back':
        await state.finish()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вернуться в меню затрат')
        await dialog_manager.start(FSMUser.expenses, mode=StartMode.NEW_STACK)
        return
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Введите сколько потратили {payment.get(call.data)}')
    async with state.proxy() as data:
        data['expenses_money'] = call.data
    await FSMUser.user_expenses.set()


@dp.message_handler(Number(), state=FSMUser.user_expenses)
@logger.catch()
async def user_expenses(message: Message, state: FSMContext) -> None:
    """
    Функция для подтверждения веденных данных
    :param message:
    :param state:
    :return:
    """
    logger.info(f'Денег потрачено: {message.text}')

    async with state.proxy() as data:
        data['user_expenses'] = message.text
        expenses_name = data.get('expenses_add')
        type_of_payment = data.get('expenses_money')
    money_sum = message.text
    if len(message.text.split()) == 2:
        money_sum = int(message.text.split()[0]) + int(message.text.split()[1])
    await message.answer(f'Вы потратили на {expenses_name}'
                         f'\nВид оплаты: {payment.get(type_of_payment)}'
                         f'\nКол-во денег потрачено: {money_sum}', reply_markup=nav.marcup_yes_no)
    await FSMUser.expenses_confirmation.set()


@dp.callback_query_handler(state=FSMUser.expenses_confirmation)
async def exp_confirmation(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):

    if call.data in 'yes':
        logger.info(f'Пользователь {call.from_user.first_name} подтвердил запись')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Данные записаны')
        async with state.proxy() as data:
            expenses_name = data.get('expenses_add')
            type_of_payment = data.get('expenses_money')
            money = data['user_expenses']
        user_id = RegisterUser.get(RegisterUser.user_id == call.from_user.id)
        cash = 0
        card = 0
        if type_of_payment == 'card':
            card = int(money)
        elif type_of_payment == 'cash':
            cash = int(money)
        elif type_of_payment == 'card_cash' and len(money.split()) == 2:
            card = int(money.split()[1])
            cash = int(money.split()[0])
        try:
            money = WalletDB.get(WalletDB.user_id == user_id.id)
            money_card = money.money_card
            money_cash = money.money_cash
            credit = money.money_credit
            if money_card - card >= 0 and money_cash - cash >= 0:
                money_cash -= cash
                money_card -= card
            else:
                await call.message.answer(f'Нехватает оплаты {payment.get(type_of_payment)}'
                                          f'\nЗайдите в настройки и распределите баланс между наличными и картой')
                await state.finish()
                async with state.proxy() as data:
                    data['user_id'] = call.from_user.id
                await dialog_manager.start(FSMUser.home, mode=StartMode.NEW_STACK)
                return
            if expenses_name.startswith('кредит'):
                logger.info(f'Кредит погашен')
                credit = 0
            wall = WalletDB.update(money_card=money_card, money_cash=money_cash,
                                   money_credit=credit).where(WalletDB.user_id == user_id.id)
            wall.execute()
        except DoesNotExist as exp:
            logger.info(exp.__class__.__name__, exp)
            await call.message.answer('Нет записей в таблице 👛 кошелька\nПополните кошелек и попробуйте еще раз')
        except ImproperlyConfigured as exc:
            logger.error(f'{exc.__class__.__name__} {exc}')

        expenses = None
        try:
            expenses, created = Expenses.get_or_create(name=expenses_name, user_id=user_id.id)
        except OperationalError as exc:
            logger.error(f'{exc.__class__.__name__}, {exc}')
        WalletExpenses.create(user_id=user_id.id, expenses_id=expenses, money_card=card, money_cash=cash)
        await state.finish()
        await dialog_manager.start(FSMUser.expenses, mode=StartMode.NEW_STACK)
    else:
        logger.info(f'Пользователь {call.from_user.first_name} отменил запись')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Запись отменена')
        await state.finish()
        await dialog_manager.start(FSMUser.expenses, mode=StartMode.NEW_STACK)
