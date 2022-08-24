from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMUser(StatesGroup):
    profit = State()
    user_profit = State()
    expenses = State()
    expenses_other = State()
    user_expenses = State()
    report = State()
