from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from states.state_user import FSMUser
from database.accountant import UserSubscription, RegisterUser
from peewee import DoesNotExist, OperationalError
from logger.log import logger
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Button
import time


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
    try:
        user_count = UserSubscription.select().where(UserSubscription.time_sub > time.time()).count()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Кол-во подписчиков <b>{user_count}</b>')
        await dialog_manager.data.get('state').finish()
    except DoesNotExist as exc:
        logger.info(f'Таблица пользователей с подпиской пуста {exc.__class__.__name__}')
