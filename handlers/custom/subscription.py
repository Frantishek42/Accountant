# from datetime import datetime
import time
import datetime
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext
from config_data.config import YOOTOKEN
from loader import dp, bot
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, ShippingQuery, ShippingOption
import keyboards.inline as nav
from states.state_user import FSMUser
from database.accountant import UserSubscription, RegisterUser
from peewee import *
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from logger.log import logger
import asyncio


def days_to_second(days):
    return days * 24 * 60 * 60


async def add_user_private(id_user: int, days: int):
    user_id = None
    time_sub = int(time.time())
    private = None
    try:
        user_id = RegisterUser.get(RegisterUser.user_id == id_user)
        private = UserSubscription.get(UserSubscription.user_id == user_id.id)
    except DoesNotExist as exc:
        logger.info(f'Таблице нет записей')
    if private is not None:
        time_sub += days_to_second(days)
        if int(private.time_sub) >= int(time.time()):
            time_sub = int(private.time_sub) + days_to_second(days)
        private = UserSubscription.update(time_sub=time_sub).where(UserSubscription.user_id == user_id.id)
        private.execute()
    else:
        UserSubscription.create(user_id=user_id.id, time_sub=int(time_sub) + days_to_second(days))


async def get_subscription(call: CallbackQuery, buttons: Button, dialog_manager: DialogManager):

    await dialog_manager.data.get('state').reset_state(with_data=False)
    user_id = RegisterUser.get(RegisterUser.user_id == call.from_user.id)
    text = ''
    try:
        time_sub = UserSubscription.get(UserSubscription.user_id == user_id.id)
        middle_time = int(time_sub.time_sub) - int(time.time())
        if middle_time > 0:
            dt = str(datetime.timedelta(seconds=middle_time))
            dt = dt.replace('days', 'дней')
            dt = dt.replace('day', 'день')
            text = f'Подписка подключена осталось: <b>{dt}</b>'
        else:
            text = 'Подписка не подключена'
    except DoesNotExist as exc:
        logger.info(f'В таблице подписки нет записей')
    finally:
        await dialog_manager.done()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Вы зашли в меню подписка'
                                         f'\n{text}', reply_markup=nav.marcup_subscription)
        await FSMUser.subscription.set()


@dp.callback_query_handler(state=FSMUser.subscription)
async def user_subscription(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager) -> None:
    """

    :param dialog_manager:
    :param state:
    :param call:
    :return:
    """
    if call.data in 'activate':
        logger.info(f'Пользователь {call.from_user.first_name} выбрал подключить или продлить прописку')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Выберите на какой срок подключить', reply_markup=nav.marcup_number)
        await FSMUser.payment.set()
    elif call.data in 'home':
        logger.info(f'Пользователь {call.from_user.first_name} вернулся в меню настройки')
        await state.finish()
        async with state.proxy() as data:
            data['user_id'] = call.from_user.id
        message = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Вы вернулись в Главное меню')
        await dialog_manager.start(FSMUser.home, mode=StartMode.NEW_STACK)
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=message.message_id)


@dp.callback_query_handler(state=FSMUser.payment)
async def get_payment(call: CallbackQuery):
    """
    Функция для оплаты подписки
    :param call:
    :return:
    """
    if call.data == 'month':
        logger.info(f"Пользователь {call.from_user.first_name} выбрал месячную подписку")
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_invoice(call.message.chat.id, title='Оформление подписки',
                               description='Активация подписки на 1 месяц',
                               payload='month',
                               provider_token=YOOTOKEN,
                               start_parameter="month_subscription",
                               currency="rub",
                               prices=[LabeledPrice(label='Подписка на 1 месяц', amount=10000)])
    elif call.data == 'three_month':
        logger.info(f"Пользователь {call.from_user.first_name} выбрал 3х месячную подписку")
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_invoice(call.message.chat.id, title='Оформление подписки',
                               description='Активация подписки на 3 месяц',
                               payload='three_month',
                               provider_token=YOOTOKEN,
                               start_parameter="three_month_subscription",
                               currency="rub",
                               prices=[LabeledPrice(label='Подписка на 3 месяц', amount=28000)])
    elif call.data == 'half_year':
        logger.info(f"Пользователь {call.from_user.first_name} выбрал полугодовую подписку")
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_invoice(call.message.chat.id, title='Оформление подписки',
                               description='Активация подписки на полгода',
                               payload='half_year',
                               provider_token=YOOTOKEN,
                               start_parameter="half_year_subscription",
                               currency="rub",
                               prices=[LabeledPrice(label='Подписка на полгода', amount=55000)])
    elif call.data == 'year':
        logger.info(f"Пользователь {call.from_user.first_name} выбрал годовую подписку")
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_invoice(call.message.chat.id, title='Оформление подписки',
                               description='Активация подписки на 1 год',
                               payload='year',
                               provider_token=YOOTOKEN,
                               start_parameter="year_subscription",
                               currency="rub",
                               prices=[LabeledPrice(label='Подписка на 1 год', amount=110000)])


@dp.pre_checkout_query_handler(state="*")
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery) -> None:
    logger.info('Идет проверка ')
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state='*')
async def process_pay(message: Message, state: FSMContext, dialog_manager: DialogManager):
    if message.successful_payment.invoice_payload == 'month':
        await add_user_private(message.from_user.id, 30)
    elif message.successful_payment.invoice_payload == 'three_month':
        await add_user_private(message.from_user.id, 90)
    elif message.successful_payment.invoice_payload == 'half_year':
        await add_user_private(message.from_user.id, 180)
    elif message.successful_payment.invoice_payload == 'year':
        await add_user_private(message.from_user.id, 365)
    await state.reset_state(with_data=False)
    await dialog_manager.start(FSMUser.home, mode=StartMode.NEW_STACK)
