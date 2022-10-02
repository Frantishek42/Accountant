from aiogram.types import Message, CallbackQuery
from states.state_user import FSMUser
from logger.log import logger
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Button


@logger.catch()
async def home_menu(call: CallbackQuery, button: Button, dialog_manager: DialogManager):

    async with dialog_manager.data.get('state').proxy() as data:
        data['user_id'] = call.from_user.id

    await dialog_manager.dialog().switch_to(FSMUser.home)
    logger.info(f'Пользователь {call.from_user.first_name} зашел в главное меню')
