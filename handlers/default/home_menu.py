from typing import Dict
from config_data.config import ADMIN
from aiogram.types import Message, CallbackQuery
from handlers.custom.admin import admin, get_count_user, get_count_subscriber
from handlers.custom.auto_payment import auto_payment_new
from handlers.custom.expenses import get_expenses, call_expenses
from handlers.custom.home import home_menu
from handlers.custom.profit import profit, call_profit
from handlers.custom.settings import user_settings, get_settings
from handlers.custom.subscription import get_subscription
from states.state_user import FSMUser
from aiogram.dispatcher import FSMContext
from loader import *
from logger.log import logger
from database.accountant import RegisterUser, WalletDB, UserSubscription
from aiogram_dialog import Window, Dialog, StartMode, DialogManager
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Button, Row, Group, Column
from loader import registry
from peewee import DoesNotExist
from aiogram_dialog.widgets.when import Whenable
import time
import datetime
from aiogram_dialog.exceptions import UnknownIntent


async def get_admin(state: FSMContext, **kwargs):
    async with state.proxy() as data:
        user_first_name = data.get('user_name')
        user_id = data.get('user_id')
    return {
        "name": f'Администратор {user_first_name}',
        'user_id': user_id,
        "extended": True,
    }


def is_admin(data: Dict, widget: Whenable, manager: DialogManager):
    return data.get("user_id") == int(ADMIN)


@logger.catch()
async def get_data(state: FSMContext, **kwargs):

    async with state.proxy() as data:
        user_id = data.get('user_id')
    user = RegisterUser.get(RegisterUser.user_id == user_id)
    try:
        time_sub = UserSubscription.get(UserSubscription.user_id == user.id)
        middle_time = int(time_sub.time_sub) - int(time.time())
        if middle_time > 0:
            dt = datetime.timedelta(seconds=middle_time)
            dt = str(dt).replace('days', 'дней')
            dt = dt.replace('day', 'день')
            text = f'Подписка подключена осталось: <b>{dt}</b>'
        else:
            text = 'Подписка не подключена'
    except DoesNotExist as exc:
        logger.info(f'{exc.__class__.__name__} {exc}')
        text = 'Подписка не подключена'
    card, cash, credit = 0, 0, 0
    try:
        user_money = WalletDB.get(WalletDB.user_id == user.id)
        card, cash, credit = user_money.money_card, user_money.money_cash, user_money.money_credit

    except DoesNotExist as exc:
        logger.info(f'{exc.__class__.__name__} {exc}')
    return {'name': (f"{text}\n💳 Карта: <b>{card}</b> 💵 Наличные: <b>{cash}"
                     f"\n</b> 🏦 Кредит: <b>{credit}</b> 💰 Общая: <b>{card + cash - credit}</b>")
            }


@logger.catch()
async def go_clicked(call: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Go click')

try:
    main_window = Dialog(
        Window(
            Multi(
                Const("≡ Меню"),
            ),
            Group(
                Column(
                    Button(Const("≡ Главное меню"), id="home", on_click=home_menu),
                    Button(Const("⚙ Настройки"), id="settings", on_click=go_clicked),
                    when="extended",
                ),
                Button(Const("Admin"), id="admin", on_click=admin, when=is_admin),
            ),
            state=FSMUser.start,
            getter=get_admin
        ),
        Window(
            Multi(
                Const("⚙ Настройки"),
            ),
            Group(
                Row(
                    Button(Const("💰 Бюджет"), id="budget", on_click=get_settings),
                    Button(Const("🗞 Автоплатеж"), id="auto_payment", on_click=auto_payment_new),

                ),
                Button(Const("≡ Главное меню"), id="home", on_click=home_menu),
            ),
            state=FSMUser.settings,
        ),
        Window(
            Multi(
                Format("<b>≡ Главное меню</b>\n\n{name}"),
            ),
            Group(
                Row(
                    Button(Const("📈 Прибыль"), id="profit", on_click=profit),
                    Button(Const("📉 Затраты"), id="expenses", on_click=get_expenses),
                    Button(Const("⌛ Автоплатеж"), id="auto_payment", on_click=auto_payment_new),
                ),
                Button(Const("♥ Подписка"), id="subscription", on_click=get_subscription),
                Button(Const("📖 Отчет"), id="report", on_click=go_clicked),
                Button(Const("⚙ Настройки"), id="settings", on_click=user_settings),
            ),
            state=FSMUser.home,
            getter=get_data,

        ),
        Window(
            Const("Вы зашли в меню прибыль"),
            Row(
                Button(Const("🛠 Зарплату"), id="salary", on_click=call_profit),
                Button(Const("🪛 Подработку"), id="part_time_job", on_click=call_profit),
            ),
            Row(
                Button(Const("🎁 Подарок"), id="gift", on_click=call_profit),
                Button(Const("🧮 Продажу"), id="sale", on_click=call_profit),
            ),
            Button(Const("≡ Главное меню"), id="home", on_click=home_menu),
            state=FSMUser.profit,
        ),
        Window(
            Const("Вы зашли в меню затраты"),
            Row(
                Button(Const("🍱 Продукты"), id="products", on_click=call_expenses),
                Button(Const("🍺 Алкоголь"), id="alcohol", on_click=call_expenses),
                Button(Const("🏠 ЖКХ"), id="communal", on_click=call_expenses),
            ),
            Row(
                Button(Const("🏎 АЗС"), id="gas_station", on_click=call_expenses),
                Button(Const("🚗 Машина"), id="car", on_click=call_expenses),
                Button(Const("🌐 Инт. магазин"), id="online_store", on_click=call_expenses),
            ),
            Row(
                Button(Const("👕 Одежда"), id="clothes", on_click=call_expenses),
                Button(Const("☎ Связь"), id="connection", on_click=call_expenses),
                Button(Const("🏖 Отдых"), id="rest", on_click=call_expenses),
            ),
            Button(Const("✙ Добавить / Выбрать свое"), id="add_choose", on_click=call_expenses),
            Button(Const("≡ Главное меню"), id="home", on_click=home_menu),
            state=FSMUser.expenses,
        ),
        Window(
            Const("Admin панель"),
            Button(Const('Кол-во пользователей'), id='count_user', on_click=get_count_user),
            Button(Const('Кол-во подписчиков'), id='count_subscriber', on_click=get_count_subscriber),
            state=FSMUser.admin
        ),
    )

    registry.register(main_window)
except UnknownIntent as exc:
    logger.error(f'Что то пошло не так {exc.__class__.__name__}')
