from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Main menu ---

profit = KeyboardButton('๐ ะัะธะฑัะปั')
expenses = KeyboardButton('๐ ะะฐััะฐัั')
wallet = KeyboardButton('๐ ะะพัะตะปะตะบ')
report = KeyboardButton('๐ ะััะตั')
marcup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(profit, expenses, wallet, report)

