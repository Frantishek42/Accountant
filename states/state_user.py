from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMUser(StatesGroup):
    """
    Класс для создания состоянии
    """
    profit = State()
    profit_money = State()
    user_profit = State()
    expenses = State()
    expenses_other = State()
    expenses_money = State()
    user_expenses = State()
    expenses_card_cash = State()
    report = State()
