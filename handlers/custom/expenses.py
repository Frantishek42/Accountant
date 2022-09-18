from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import ExpensesFilter, Number
import keyboards.inline as nav
from keyboards.inline import marcup_auto_payment
from states.state_user import FSMUser
from database.expensesdb import *
from database.walletdb import WalletDB
from logger.log import logger
from database.auto_payment import AutoPayment

expenses_user = {
    'products': 'продукты', 'alcohol': 'алкоголь', 'chemistry': 'химия', 'communal': 'ЖКХ', 'credit': 'кредит',
    'gas_station': 'АЗС', 'car': 'машина', 'online_store': 'интернет магазин', 'auto_payment': 'Автоплатеж',
    'clothes': 'Одежда', 'connection': 'Связь', 'rest': 'Отдых', 'eyes': 'Глаза', 'materials': 'Материалы',
    'internet': 'Интернет, ТВ', 'gifts': 'Подарки', 'animals': 'Животные', 'the_others': 'Другие'
}


@dp.message_handler(ExpensesFilter(), state='*')
async def get_expenses(message: Message) -> None:
    """
    Функция для приема команды Затраты
    :param message: Message
    :return:
    """
    logger.info('Вы зашли в команду Затраты')
    await FSMUser.expenses.set()
    await message.answer('Что добавить?', reply_markup=nav.marcup_expenses)


@dp.callback_query_handler(state=FSMUser.expenses)
async def call_expenses(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция отлавливает кнопки marcup_expenses
    :param call:
    :param state:
    :return:
    """
    logger.info(f'Затраты на {expenses_user.get(call.data)}')
    answer = call.data
    async with state.proxy() as data:
        data['expenses'] = expenses_user.get(answer)
    if call.data == 'further':
        await FSMUser.expenses_other.set()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Что добавить?', reply_markup=nav.marcup_other)
        return
    elif call.data == 'auto_payment':
        AutoPayment.create_table()
        user_count = AutoPayment.select().where(AutoPayment.user_id == call.from_user.id).count()
        if user_count > 0:
            await FSMUser.expenses_auto_payment.set()
            marcup_auto = marcup_auto_payment(call.message)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Выберите что хотите сделать', reply_markup=marcup_auto)
            return
        else:
            await FSMUser.expenses_auto_payment.set()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Не создан не один автоплатеж. Создать?',
                                        reply_markup=nav.marcup_yes_no)
            return

    await FSMUser.expenses_money.set()
    prefix = 'На'
    if call.data == 'online_store':
        prefix = 'В'
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'{prefix} {expenses_user.get(call.data)}')
    await call.message.answer('Выберите категорию', reply_markup=nav.marcup_money)


@dp.callback_query_handler(state=FSMUser.expenses_auto_payment)
async def auto_payment_new(call: CallbackQuery):
    """
    Функция для добавления или изменения автоплатежа
    :param call:
    :return:
    """
    logger.info(f'Создать автоплатеж {"да" if call.data == "yes" else "нет"}')
    if call.data in ['yes', 'auto_add']:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Введите названия автоплатежа')
        await FSMUser.expenses_auto_payment_create_name.set()
    elif call.data == 'no':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Что добавить?', reply_markup=nav.marcup_expenses)
        await FSMUser.expenses.set()
        return


@dp.message_handler(state=FSMUser.expenses_auto_payment_create_name)
async def auto_payment_create_name(message: Message, state: FSMContext) -> None:
    logger.info(f'Названия платежа {message.text}')
    async with state.proxy() as data:
        data['expenses_auto_payment_create_name'] = message.text
    await message.answer('Введите сумму автоплатежа')
    await FSMUser.expenses_auto_payment_create_price.set()


@dp.message_handler(Number(), state=FSMUser.expenses_auto_payment_create_price)
async def auto_payment_create_price(message: Message, state: FSMContext) -> None:
    logger.info(f'Сумма автоплатежа {message.text}')
    async with state.proxy() as data:
        data['expenses_auto_payment_create_price'] = message.text
    await message.answer('Введите день списания')
    await FSMUser.expenses_auto_payment_create_day.set()


@dp.message_handler(Number(), state=FSMUser.expenses_auto_payment_create_day)
async def auto_payment_create_price(message: Message, state: FSMContext) -> None:
    logger.info(f'День когда сработает автоплатеж: {message.text}')
    auto_payment_day = message.text
    async with state.proxy() as data:
        auto_payment_name = data.get('expenses_auto_payment_create_name')
        auto_payment_price = data.get('expenses_auto_payment_create_price')
    AutoPayment.create(user_id=message.from_user.id, name=auto_payment_name, price=auto_payment_price,
                       day_of_debiting=auto_payment_day)
    await message.answer(f'Автоплатеж: {auto_payment_name}'
                         f'\nСумма: {auto_payment_price}'
                         f'\nДень: {auto_payment_day} '
                         f'\nПодключен!!!')
    await state.finish()


@dp.callback_query_handler(state=FSMUser.expenses_other)
async def other(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция отлавливает кнопки marcup_other
    :param call:
    :param state:
    :return:
    """
    logger.info(f'Затраты на {expenses_user.get(call.data)}')
    if call.data == 'back':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Что добавить?', reply_markup=nav.marcup_expenses)
        await FSMUser.expenses.set()
        return

    async with state.proxy() as data:
        data['expenses'] = expenses_user.get(call.data)
    await FSMUser.expenses_money.set()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'На {expenses_user.get(call.data)}')
    await call.message.answer('Выберите категорию', reply_markup=nav.marcup_money)


@dp.callback_query_handler(state=FSMUser.expenses_money)
async def expenses_money(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция отлавливает кнопки marcup_money
    :param call:
    :param state:
    :return:
    """
    exp_money = {'card': 'картой', 'cash': 'наличными', 'card_cash': 'нал. безнал'}
    logger.info(f'Выбор категории {exp_money.get(call.data)}')

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Введите сколько потратили {exp_money.get(call.data)}')
    async with state.proxy() as data:
        data['expenses_money'] = call.data
    await FSMUser.user_expenses.set()


@dp.message_handler(Number(), state=FSMUser.user_expenses)
@logger.catch()
async def user_expenses(message: Message, state: FSMContext) -> None:
    """
    Функция для создания таблицы затрат
    :param message:
    :param state:
    :return:
    """
    logger.info(f'Денег потрачено: {message.text}')

    async with state.proxy() as data:
        expenses_name = data.get('expenses')
        money = data.get('expenses_money')

    cash = 0
    card = 0
    if money == 'card':
        card = message.text
    elif money == 'cash':
        cash = message.text
    elif money == 'card_cash' and len(message.text.split()) == 2:
        card = message.text.split()[1]
        cash = message.text.split()[0]
    else:
        await message.answer('Данные ведены неверно. Попробуйте еще раз.\nВведите через пробел нал безнал')
        return

    Expenses.create_table()
    expenses = None
    try:
        expenses, created = Expenses.get_or_create(name=expenses_name)
    except OperationalError as exc:
        logger.error(f'{exc.__class__.__name__}, {exc}')
    WalletExpenses.create_table()
    WalletExpenses.create(user_id=message.from_user.id, expenses_id=expenses, money_card=card, money_cash=cash)
    await wallet_money(message, state)
    await state.finish()


@logger.catch()
async def wallet_money(message: Message, state: FSMContext) -> None:
    """
    Функция для обновления таблицы кошелек и вывод пользователю информация о балансе

    :param state:
    :param message:
    :return:
    """
    money_expenses = message.text
    async with state.proxy() as data:
        exp_money = data.get('expenses_money')
        exp_credit = data.get('expenses')

    card = 0
    cash = 0
    if exp_money == 'card':
        card = int(money_expenses)
    elif exp_money == 'cash':
        cash = int(money_expenses)
    elif exp_money == 'card_cash':
        card = int(money_expenses.split()[1])
        cash = int(money_expenses.split()[0])
    card_cash = card + cash

    try:
        money = WalletDB.select().where(WalletDB.id == 1).get()
        money_card = money.money_card
        money_cash = money.money_cash
        credit = money.money_credit
        if exp_money == 'card' and money_card > card_cash:
            money_card -= card_cash
        elif exp_money == 'cash' and money_cash > card_cash:
            money_cash -= card_cash
        elif exp_money == 'card_cash' and money_card + money_cash > card_cash:
            money_cash -= card_cash
            money_card += money_cash
            money_cash = 0
        else:
            credit = money_card + money_cash - card_cash
            money_card = 0
            money_cash = 0
            wall = WalletDB.update(money_card=0, money_cash=0, money_credit=abs(credit)).where(WalletDB.id == 1)
            wall.execute()
            await message.answer(f'Вы зашли за лимит. Задолженность составляет: <b>{abs(credit)}</b>')
        if exp_credit == 'кредит' and credit == card_cash:
            logger.info(f'Кредит погашен')
            credit = 0
        wall = WalletDB.update(money_card=money_card, money_cash=money_cash,
                               money_credit=credit).where(WalletDB.id == 1)
        wall.execute()
        await message.answer(
            f'Ваш кошелек похудел на <b>{card_cash}</b>'
            f'\nДенег в кошелке осталось: '
            f'\nНа карте: <b>{money_card}</b> ₱'
            f'\nНаличные: <b>{money_cash}</b> ₱'
            f'\nЗадолженность по кредитке: <b>{abs(credit)}</b> ₱'
            f'\nОбщая: <b>{money_card + money_cash - credit}</b> ₱'
        )
    except OperationalError as exp:
        logger.error(exp.__class__.__name__, exp)
        await message.answer('База данных кошелек не создана или удалена')
