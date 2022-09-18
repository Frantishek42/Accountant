from aiogram.types import Message

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# <--- InlineKeyboardButton для menu profit --->
from database.auto_payment import AutoPayment

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
auto_payment = InlineKeyboardButton(text='🗞 Автоплатеж', callback_data='auto_payment')
further = InlineKeyboardButton(text='🔜 Далее', callback_data='further')

marcup_expenses.add(products, alcohol, chemistry, communal, credit, gas_station,
                    car, online_store, auto_payment, further)


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


# <--- InlineKeyboardButton категория наличных и безналичных для затрат--->

marcup_yes_no = InlineKeyboardMarkup(row_width=3)
yes = InlineKeyboardButton(text='Да', callback_data='yes')
no = InlineKeyboardButton(text='Нет', callback_data='no')
marcup_yes_no.add(yes, no)


def marcup_auto_payment(message: Message):
    marcup_auto = InlineKeyboardMarkup(row_width=3)
    auto = AutoPayment.select().where(AutoPayment.user_id == message.chat.id)
    auto_list = [InlineKeyboardButton(text=payment.name, callback_data=payment.id) for payment in auto]
    auto_add = InlineKeyboardButton(text='Добавить', callback_data='auto_add')
    back_auto = InlineKeyboardButton(text='🔙 Назад', callback_data='back')
    marcup_auto.add(*auto_list, auto_add, back_auto)
    return marcup_auto
