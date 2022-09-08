from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# <--- InlineKeyboardButton для menu profit --->

marcup_profit = InlineKeyboardMarkup(row_width=2)
salary = InlineKeyboardButton(text='🛠 Зарплату', callback_data='salary')
part_time_job = InlineKeyboardButton(text='🪛 Подработку', callback_data='part_time_job')
sale = InlineKeyboardButton(text='🧮 Продажу', callback_data='sale')
marcup_profit.add(salary, part_time_job, sale)


# <--- InlineKeyboardButton для menu expenses --->

marcup_expenses = InlineKeyboardMarkup(row_width=3)
products = InlineKeyboardButton(text='🍱 Продукты', callback_data='products')
alcohol = InlineKeyboardButton(text='🍺 Алкоголь', callback_data='alcohol')
chemistry = InlineKeyboardButton(text='🔴 Химия', callback_data='chemistry')
communal = InlineKeyboardButton(text='🏠 ЖКХ', callback_data='communal')
credit = InlineKeyboardButton(text='🏦 Кредиты', callback_data='credit')
gas_station = InlineKeyboardButton(text='🏎 АЗС', callback_data='gas_station')
car = InlineKeyboardButton(text='🚗 Машина', callback_data='car')
online_store = InlineKeyboardButton(text='🌐 Инт. магазин', callback_data='online_store')
other = InlineKeyboardButton(text='🗞 Прочее', callback_data='other')

marcup_expenses.add(products, alcohol, chemistry, communal, credit, gas_station, car, online_store, other)


# <--- InlineKeyboardButton для menu expenses other --->

marcup_other = InlineKeyboardMarkup(row_width=3)
clothes = InlineKeyboardButton(text='👕 Одежда', callback_data='clothes')
connection = InlineKeyboardButton(text='☎ Связь', callback_data='connection')
rest = InlineKeyboardButton(text='🏖 Отдых', callback_data='rest')
eyes = InlineKeyboardButton(text='👁 Глаза', callback_data='eyes')
materials = InlineKeyboardButton(text='💅 Материалы', callback_data='materials')
internet = InlineKeyboardButton(text='🌐 Интернет, ТВ', callback_data='internet')
gifts = InlineKeyboardButton(text='🎁 Подарки', callback_data='gifts')
animals = InlineKeyboardButton(text='🐕 Животные', callback_data='animals')
the_others = InlineKeyboardButton(text='💸 Другие', callback_data='the_others')
back = InlineKeyboardButton(text='🔙 Назад', callback_data='back')

marcup_other.add(clothes, connection, rest, eyes, materials, internet, gifts, animals, the_others, back)


# <--- InlineKeyboardButton категория наличных и безналичных --->

marcup_money = InlineKeyboardMarkup(row_width=2)
money_card = InlineKeyboardButton(text='💳 Карта', callback_data='card')
money_cash = InlineKeyboardButton(text='💵 Наличные', callback_data='cash')
money_cash_card = InlineKeyboardButton(text='💰 Нал. безнал', callback_data='card_cash')
marcup_money.add(money_card, money_cash, money_cash_card)


# # <--- InlineKeyboardButton категория наличных и безналичных для затрат--->
#
# marcup_money_expenses = InlineKeyboardMarkup(row_width=3)
# money_card = InlineKeyboardButton(text='Карта', callback_data='card')
# money_cash = InlineKeyboardButton(text='Наличные', callback_data='cash')
# money_cash_card = InlineKeyboardButton(text='Нал. безнал', callback_data='card_cash')
# marcup_money_expenses.add(money_card, money_cash, money_cash_card)
