from aiogram.types import Message
from peewee import OperationalError, DoesNotExist
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from logger.log import logger
import math
from database.accountant import RegisterUser, Expenses, AutoPayment


# <--- InlineKeyboardButton вид оплаты наличных и безналичных --->

marcup_money = InlineKeyboardMarkup(row_width=2)
money_card = InlineKeyboardButton(text='💳 Карта', callback_data='card')
money_cash = InlineKeyboardButton(text='💵 Наличные', callback_data='cash')
money_cash_card = InlineKeyboardButton(text='💰 Нал. безнал', callback_data='card_cash')
back_auto = InlineKeyboardButton(text='🔙 Назад', callback_data='back')
marcup_money.add(money_card, money_cash, money_cash_card)
marcup_money.add(back_auto)

# <--- InlineKeyboardButton для подтверждения пользователя--->

marcup_yes_no = InlineKeyboardMarkup(row_width=3)
yes = InlineKeyboardButton(text='Да', callback_data='yes')
no = InlineKeyboardButton(text='Нет', callback_data='no')
marcup_yes_no.add(yes, no)


# <--- InlineKeyboardButton для бюджета --->

marcup_budget = InlineKeyboardMarkup(row_width=3)
cash_withdrawal = InlineKeyboardButton(text='💵 Снятие наличных', callback_data='cash_withdrawal')
put_card = InlineKeyboardButton(text='💳 Положить на карту', callback_data='put_card')
setting = InlineKeyboardButton(text='⚙ Настройки', callback_data='settings')
marcup_budget.add(cash_withdrawal, put_card)
marcup_budget.add(setting)


# ---> InlineKeyboardButton для меню подписки --->

marcup_subscription = InlineKeyboardMarkup(row_width=2)
activate = InlineKeyboardButton(text='✙ Подключить/Продлить', callback_data='activate')
home = InlineKeyboardButton(text='≡ Главное меню', callback_data='home')
marcup_subscription.add(activate)
marcup_subscription.add(home)


# --->  InlineKeyboardButton  --->

marcup_number = InlineKeyboardMarkup(row_width=2)
month = InlineKeyboardButton(text='Месяц: 100руб.', callback_data='month')
three_month = InlineKeyboardButton(text='Три месяца: 280руб.', callback_data='three_month')
half_year = InlineKeyboardButton(text='Пол года: 550руб.', callback_data='half_year')
year = InlineKeyboardButton(text='Год: 1100руб.', callback_data='year')
back = InlineKeyboardButton(text='🔙 Назад', callback_data='back')
marcup_number.add(month, three_month, half_year, year)
marcup_number.add(back)


def marcup_auto_payment(message: Message):
    marcup_auto = InlineKeyboardMarkup(row_width=3)
    auto_list = []
    try:
        auto = AutoPayment.select().where(AutoPayment.user_id == message.chat.id).order_by(AutoPayment.name)
        auto_list = [InlineKeyboardButton(text=payment.name, callback_data=payment.id) for payment in auto]
    except (OperationalError, DoesNotExist) as exc:
        logger.error(f'{exc.__class__.__name__} {exc}')
    finally:
        auto_add = InlineKeyboardButton(text='✙ Добавить', callback_data='auto_add')
        home = InlineKeyboardButton(text='≡ Главное меню', callback_data='home')
        marcup_auto.add(*auto_list)
        marcup_auto.add(auto_add)
        marcup_auto.add(home)
    return marcup_auto


@logger.catch()
def marcup_expenses_user(message: Message, prev=0, next_=1):
    user_id = RegisterUser.get(RegisterUser.user_id == message.chat.id)
    prev_page = InlineKeyboardButton(text='«', callback_data=f'prev:{prev}')
    next_page = InlineKeyboardButton(text='»', callback_data=f'next:{next_}')
    page_button = InlineKeyboardButton(text=f'{next_}', callback_data=f'{next_}')
    exp_buttons = []
    try:
        expenses_user = Expenses.select().where(Expenses.user_id == user_id.id).order_by(Expenses.name)
        page = math.ceil(expenses_user.count() / 3 / 3)
        next_page = InlineKeyboardButton(text='»', callback_data=f'next:{next_}:{page}')
        count = 0
        exp_count = 0
        for i_page in range(page):
            if next_ == i_page+1:
                for ind, exp in enumerate(expenses_user):
                    if exp_count <= ind:
                        count += 1
                        exp_buttons.append(InlineKeyboardButton(text=exp.name, callback_data=exp.name))
                    if count == 9:
                        break
                break
            exp_count += 9
        if len(exp_buttons) < 9:
            for i in range(9 - len(exp_buttons)):
                exp_buttons.append(InlineKeyboardButton(text=' ', callback_data=' '))
    except (OperationalError, DoesNotExist) as exc:
        logger.error(f'{exc}')
    finally:
        marcup_exp = InlineKeyboardMarkup(row_width=3)
        add = InlineKeyboardButton(text='✙ Добавить', callback_data='add')
        back = InlineKeyboardButton(text='🔙 Назад', callback_data='back')
        marcup_exp.add(*exp_buttons)
        marcup_exp.add(prev_page, page_button,  next_page)
        marcup_exp.add(add)
        marcup_exp.add(back)
    return marcup_exp
