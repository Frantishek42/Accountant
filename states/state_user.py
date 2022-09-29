from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMUser(StatesGroup):
    """
    Класс для создания состоянии
    """
    start = State()
    user_id = State()
    user_name = State()
    admin = State()
    home = State()
    register_user = State()
    profit = State()
    profit_money = State()
    user_profit = State()
    expenses = State()
    other = State()
    expenses_add = State()
    expenses_money = State()
    user_expenses = State()
    expenses_card_cash = State()
    expenses_auto_payment = State()
    expenses_auto_payment_create_name = State()
    expenses_auto_payment_create_price = State()
    expenses_auto_payment_create_day = State()
    report = State()


class FSStart(StatesGroup):
    """

    """
    start = State()
    register_user = State()


class FSExpenses(StatesGroup):
    """

    """
    other = State()
