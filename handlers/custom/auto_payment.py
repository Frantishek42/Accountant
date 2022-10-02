from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Number, UserSubscriptionFilter, AutoPaymentFilter
from keyboards.inline import marcup_auto_payment
from states.state_user import FSMUser
from database.accountant import AutoPayment, RegisterUser, UserSubscription
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from logger.log import logger
from peewee import DoesNotExist, OperationalError
import time


async def auto_payment_new(call: CallbackQuery, buttons: Button, dialog_manager: DialogManager) -> None:
    """
    Функция для добавления или изменения автоплатежа
    :param buttons:
    :param dialog_manager:
    :param call:
    :return:
    """
    # user_id = RegisterUser.get(RegisterUser.user_id == call.from_user.id)
    # try:
    #     time_sub = UserSubscription.get(UserSubscription.user_id == user_id.id)
    #     middle_time = int(time_sub) - int(time.time())
    if UserSubscription().get_time_sub(call.from_user.id):
        await dialog_manager.done()
        logger.info(f'Пользователь {call.from_user.first_name} зашел в меню автоплатежи')

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вы зашли в меню автоплатежи',
                                    reply_markup=marcup_auto_payment(call.message))
        await FSMUser.auto_payment.set()
        return
    # except DoesNotExist as exc:
    #     logger.info(f'{exc.__class__.__name__} {exc}')
    # except OperationalError as exc:
    #     logger.error(f"{exc.__class__.__name__} {exc}")
    await call.answer('Это функция не доступна 🛑 для Вас'
                      f'\n{call.from_user.first_name} Вы не оплатили подписку', show_alert=True)


@dp.callback_query_handler(state=FSMUser.auto_payment)
async def get_auto_payment(call: CallbackQuery, dialog_manager: DialogManager) -> None:
    """

    :param dialog_manager:
    :param call:
    :return:
    """
    if call.data in 'auto_add':
        logger.info(f'Пользователь {call.from_user.first_name} зашел добавить автоплатеж')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Введите название автоплатежа')
        await FSMUser.auto_payment_create_name.set()
    elif call.data in 'home':
        logger.info(f'Пользователь {call.from_user.first_name} вернулся в главное меню')
        await dialog_manager.data.get('state').finish()
        async with dialog_manager.data.get('state').proxy() as data:
            data['user_id'] = call.from_user.id
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вы вернулись в главное меню')
        await dialog_manager.start(FSMUser.home, mode=StartMode.NEW_STACK)


@dp.message_handler(state=FSMUser.auto_payment_create_name)
async def auto_payment_create_name(message: Message, state: FSMContext) -> None:
    logger.info(f'Названия платежа {message.text}')
    async with state.proxy() as data:
        data['expenses_auto_payment_create_name'] = message.text
    await message.answer('Введите сумму автоплатежа')
    await FSMUser.auto_payment_create_price.set()


@dp.message_handler(Number(), state=FSMUser.auto_payment_create_price)
async def auto_payment_create_price(message: Message, state: FSMContext) -> None:
    logger.info(f'Сумма автоплатежа {message.text}')
    async with state.proxy() as data:
        data['expenses_auto_payment_create_price'] = message.text
    await message.answer('Введите день списания')
    await FSMUser.auto_payment_create_day.set()


@dp.message_handler(Number(), state=FSMUser.auto_payment_create_day)
async def auto_payment_create_price(message: Message, state: FSMContext, dialog_manager: DialogManager) -> None:
    logger.info(f'День когда сработает автоплатеж: {message.text}')
    auto_payment_day = message.text
    async with state.proxy() as data:
        auto_payment_name = data.get('expenses_auto_payment_create_name')
        auto_payment_price = data.get('expenses_auto_payment_create_price')
    AutoPayment.create(user_id=message.from_user.id, name=auto_payment_name, price=auto_payment_price,
                       day_of_debiting=auto_payment_day)
    await message.answer(f'Автоплатеж: {auto_payment_name}'
                         f'\nСумма: {auto_payment_price}'
                         f'\nДень: {auto_payment_day} '
                         f'\nПодключен!!!')
    await state.finish()
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
    await dialog_manager.start(FSMUser.home, mode=StartMode.NEW_STACK)
