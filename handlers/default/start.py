from aiogram.types import Message, CallbackQuery
from filters.extension_filters import UserRegister
from states.state_user import FSMUser
from aiogram.dispatcher import FSMContext
from loader import *
from logger.log import logger
from database.accountant import RegisterUser
from aiogram_dialog import StartMode, DialogManager


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
