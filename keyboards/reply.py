from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Main menu ---

profit = KeyboardButton('📈 Прибыль')
expenses = KeyboardButton('📉 Затраты')
wallet = KeyboardButton('👛 Кошелек')
report = KeyboardButton('📖 Отчет')
marcup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(profit, expenses, wallet, report)

