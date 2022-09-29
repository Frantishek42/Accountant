from typing import Dict
from config_data.config import ADMIN
from filters.extension_filters import UserRegister
from aiogram.types import Message, CallbackQuery
from handlers.custom.admin import admin, get_count_user, get_count_subscriber
from handlers.custom.expenses import get_expenses, call_expenses
from handlers.custom.profit import profit, call_profit
from states.state_user import FSMUser
from aiogram.dispatcher import FSMContext
from loader import *
from logger.log import logger
from database.accountant import RegisterUser, WalletDB
from aiogram_dialog import Window, Dialog, StartMode, DialogManager
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Button, Row, Group, Column
from loader import registry
from peewee import DoesNotExist
from aiogram_dialog.widgets.when import Whenable


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
    if user.private:
        text = f'Подписка подключена осталось дней: {user.private_date}'
    else:
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
async def home_menu(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    async with dialog_manager.data.get('state').proxy() as data:
        data['user_id'] = call.from_user.id

    await dialog_manager.dialog().switch_to(FSMUser.home)

    logger.info(f'Пользователь {call.from_user.first_name} зашел в главное меню')


@logger.catch()
async def go_clicked(call: CallbackQuery, button: Button, manager: DialogManager):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Go click')


main_window = Dialog(
    Window(
        Multi(
            Const("≡ Меню"),
        ),
        Group(
            Column(
                Button(Const("≡ Главное меню"), id="report", on_click=home_menu),
                Button(Const("⚙ Настройка"), id="settings", on_click=go_clicked),
                when="extended",
            ),
            Button(Const("Admin"), id="admin", on_click=admin, when=is_admin),
        ),
        state=FSMUser.start,
        getter=get_admin
    ),
    Window(
        Format("<b>≡ Главное меню</b>\n\n{name}"),
        Row(
            Button(Const("📈 Прибыль"), id="profit", on_click=profit),
            Button(Const("📉 Затраты"), id="expenses", on_click=get_expenses),
            Button(Const("⌛ Автоплатеж"), id="auto_payment", on_click=go_clicked),
        ),
        Button(Const("📖 Отчет"), id="report", on_click=go_clicked),
        Button(Const("⚙ Настройка"), id="settings", on_click=go_clicked),
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
        Button(Const("≡ Главное меню"), id="nothing", on_click=home_menu),
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
        Button(Const("≡ Главное меню"), id="nothing", on_click=home_menu),
        state=FSMUser.expenses,
    ),
    Window(
        Const("Admin панель"),
        Button(Const('Кол-во пользователей'), id='count_user', on_click=get_count_user),
        Button(Const('Кол-во подписчиков'), id='count_subscriber', on_click=get_count_subscriber),
        state=FSMUser.admin
    )
)

registry.register(main_window)


@dp.message_handler(UserRegister(), commands=['start'], state='*')
@logger.catch()
async def process_start_command(message: Message, dialog_manager: DialogManager, state: FSMContext) -> None:
    """
    Функция для запуска бота
    :param state:
    :param dialog_manager:
    :param message:
    :return:
    """
    logger.info(f'Пользователь {message.from_user.first_name} зашел в меню')
    data = await state.get_data()
    if data is not None:
        await state.finish()
    await message.answer(f"Добро пожаловать {message.from_user.first_name}!")
    async with state.proxy() as data:
        data['user_name'] = message.from_user.first_name
        data['user_id'] = message.from_user.id
    await dialog_manager.start(FSMUser.start, mode=StartMode.NEW_STACK)


@dp.callback_query_handler(state=FSMUser.register_user)
@logger.catch()
async def register(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для регистрации пользователя
    :param state:
    :param call:
    :return:
    """
    if call.data == 'yes':
        logger.info(f'Регистрация пользователя {call.from_user.first_name}')
        RegisterUser.create(user_id=call.from_user.id, first_name=call.from_user.first_name)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Поздравляю 🎊 Вас <b>{call.from_user.first_name}</b>!!!'
                                         '\nВы зарегистрированы 👍'
                                         '\nЧтобы начать пользоваться ботом нажмите 👉 /start'
                                         '\nЧтобы узнать возможности бота нажмите 👉 /help')
    elif call.data == 'no':
        logger.info(f'Пользователь {call.from_user.first_name} отменил регистрацию ❌')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Для того чтоб использовать бота нужно зарегистрироваться ✅')
    await state.finish()
