from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Number
import keyboards.inline as nav
from states.state_user import FSMUser
from database.accountant import Profit, WalletProfit, WalletDB, RegisterUser
from peewee import DoesNotExist, OperationalError
from logger.log import logger
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Button


@logger.catch()
async def admin(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для приема команды Прибыль
    :param button:
    :param dialog_manager:
    :param call:
    :return:
    """
    logger.info(f'Админ {call.from_user.first_name} зашел в админ панель')
    await dialog_manager.dialog().switch_to(FSMUser.admin)


@logger.catch()
async def get_count_user(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для приема команды Прибыль
    :param button:
    :param dialog_manager:
    :param call:
    :return:
    """
    logger.info(f'Админ {call.from_user.first_name} зашел узнать кол-во пользователей')
    user_count = RegisterUser.select().count()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Кол-во пользователей <b>{user_count}</b>')
    await dialog_manager.data.get('state').finish()


@logger.catch()
async def get_count_subscriber(call: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для приема команды Прибыль
    :param button:
    :param dialog_manager:
    :param call:
    :return:
    """
    logger.info(f'Админ {call.from_user.first_name} зашел узнать кол-во подписчиков')
    user_count = RegisterUser.select().where(RegisterUser.private & True).count()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Кол-во подписчиков <b>{user_count}</b>')
    await dialog_manager.data.get('state').finish()
