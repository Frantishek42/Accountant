from asyncio import sleep
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from aiogram.types import Message, CallbackQuery
from filters.extension_filters import Number
import keyboards.inline as nav
from states.state_user import FSMUser
from database.accountant import WalletDB, RegisterUser
from peewee import DoesNotExist, OperationalError
from logger.log import logger
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Button
import asyncio


@logger.catch()
async def user_settings(call: CallbackQuery, buttons: Button, dialog_manager: DialogManager):
    """
    Функция для меню настройки
    :param call:
    :param buttons:
    :param dialog_manager:
    :return:
    """
    logger.info(f'Пользователь {call.from_user.first_name} зашел в меню')
    await dialog_manager.start(FSMUser.settings, mode=StartMode.RESET_STACK)


async def get_settings(call: CallbackQuery, buttons: Button, dialog_manager: DialogManager):

    if call.data == 'budget':
        logger.info(f'Пользователь выбрал настройки бюджета')
        user = RegisterUser.get(RegisterUser.user_id == call.from_user.id)
        card, cash = 0, 0
        try:
            user_money = WalletDB.get(WalletDB.user_id == user.id)
            card, cash = user_money.money_card, user_money.money_cash

        except DoesNotExist as exc:
            logger.info(f'{exc.__class__.__name__} {exc}')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'Выберите что хотите сделать\n\n💳 Карта: <b>{card}</b> '
                                         f'💵 Наличные: <b>{cash}</b>', reply_markup=nav.marcup_budget)
        await FSMUser.settings_budget.set()


@dp.callback_query_handler(state=FSMUser.settings_budget)
async def settings_budget(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    text = ' '
    if call.data in 'cash_withdrawal':
        text = 'снять наличные'
    elif call.data in 'put_card':
        text = 'положить на карту'
    elif call.data in 'settings':
        logger.info(f'Пользователь {call.from_user.first_name} вернулся в меню настройки')
        await state.finish()
        async with state.proxy() as data:
            data['user_id'] = call.from_user.id
        message = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Вы вернулись в меню настройки')
        await dialog_manager.start(FSMUser.settings, mode=StartMode.NEW_STACK)
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=message.message_id)
        return

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=f'Введите сумму которую хотите {text}:')
    async with state.proxy() as data:
        data['settings_budget'] = call.data

    await FSMUser.settings_budget_money.set()


@dp.message_handler(Number(), state=FSMUser.settings_budget_money)
async def settings_budget_money(message: Message, state: FSMContext, dialog_manager: DialogManager):
    data = await state.get_data()
    user_id = RegisterUser.get(RegisterUser.user_id == message.from_user.id)
    # wallet = None
    try:
        wallet = WalletDB.get(WalletDB.user_id == user_id.id)
    except (OperationalError, DoesNotExist) as exc:
        logger.error(f'{exc.__class__.__name__} {exc}')
        return
    if data.get('settings_budget') == 'cash_withdrawal' and wallet.money_card - int(message.text) >= 0:
        wallet = WalletDB.update(
            money_card=wallet.money_card - int(message.text), money_cash=int(message.text) + wallet.money_cash
        ).where(WalletDB.user_id == user_id.id)
        wallet.execute()
        with open('media/gif/atm_machine.gif', 'rb') as file:
            file_id = await bot.send_animation(chat_id=message.chat.id, animation=file, duration=None,
                                               caption=f'Снято наличных: <b>{message.text}</b> ₱')
        await sleep(3)
        await bot.delete_message(chat_id=message.chat.id, message_id=file_id.message_id)

    elif data.get('settings_budget') in 'put_card' and wallet.money_cash - int(message.text) >= 0:
        wallet = WalletDB.update(
            money_card=wallet.money_card + int(message.text), money_cash=wallet.money_cash - int(message.text)
        ).where(WalletDB.user_id == user_id.id)
        wallet.execute()
        with open('media/gif/atm_machine2.gif', 'rb') as file:
            file_id = await bot.send_animation(chat_id=message.chat.id, animation=file, duration=None,
                                               caption=f'Снято наличных: <b>{message.text}</b> ₱')
        await sleep(3)
        await bot.delete_message(chat_id=message.chat.id, message_id=file_id.message_id)
    else:
        await message.answer(f'Нехватает денег\n\n💳 Карта: <b>{wallet.money_card}</b> '
                             f'💵 Наличные: <b>{wallet.money_cash}</b>', reply_markup=nav.marcup_budget)
        await FSMUser.settings_budget.set()
        return
    await state.finish()
    await dialog_manager.start(FSMUser.settings, mode=StartMode.NEW_STACK)

