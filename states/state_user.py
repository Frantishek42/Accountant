from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMUser(StatesGroup):
    """
    Класс для создания состоянии
    """
    register_user = State()
    start = State()
    user_id = State()
    user_name = State()
    admin = State()
    home = State()
    settings = State()
    settings_budget = State()
    settings_budget_money = State()
    profit = State()
    profit_money = State()
    user_profit = State()
    expenses = State()
    other = State()
    expenses_back = State()
    expenses_add = State()
    expenses_money = State()
    user_expenses = State()
    expenses_confirmation = State()
    auto_payment = State()
    auto_payment_create_name = State()
    auto_payment_create_price = State()
    auto_payment_create_day = State()
    report = State()
    subscription = State()
    payment = State()


class FSStart(StatesGroup):
    """

    """
    start = State()
    register_user = State()


class FSExpenses(StatesGroup):
    """

    """
    other = State()
