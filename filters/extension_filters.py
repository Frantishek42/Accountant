from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from database.accountant import RegisterUser, UserSubscription
import keyboards.inline as nav
from logger.log import logger
from states.state_user import FSMUser
from peewee import DoesNotExist, OperationalError


class UserRegister(BoundFilter):
    """
    Дочерний класс UserID родитель BoundFilter создан для фильтрации id пользователя

    """

    async def check(self, message: types.Message):
        """
        Функция для проверки id пользователя
        :param message:
        :return:
        """
        try:
            user = RegisterUser.get(RegisterUser.user_id == message.from_user.id)
            logger.info(f'Пользователь {message.from_user.first_name} запускает бота')
            if user.user_id:
                return True
        except Exception as exc:
            logger.info(f'{exc.__class__.__name__}, {exc}')
            logger.info(f'Пользователь {message.from_user.first_name} в базе данных нет')
            await FSMUser.register_user.set()
            await message.answer(f'Здравствуйте {message.from_user.first_name}'
                                 f'\nВы не зарегистрированы.'
                                 '\nХотите пройти регистрацию', reply_markup=nav.marcup_yes_no)
            return False


class UserSubscriptionFilter(BoundFilter):
    """

    """
    async def check(self, call: types.CallbackQuery) -> bool:
        if call.data in 'auto_payment':
            logger.info(f'Идет проверка пользователя {call.from_user.first_name} на доступ кошелька')
            user_id = RegisterUser.get(RegisterUser.user_id == call.from_user.id)
            try:
                user_private = UserSubscription.get(UserSubscription.user_id == user_id.id)
                if user_private.private:
                    return True
            except DoesNotExist as exc:
                logger.info(f'{exc.__class__.__name__} {exc}')
            except OperationalError as exc:
                logger.error(f"{exc.__class__.__name__} {exc}")
            await call.answer('Это функция не доступна 🛑 для Вас'
                              f'\n{call.from_user.first_name} Вы не оплатили подписку', show_alert=True)
            return False


class AutoPaymentFilter(BoundFilter):
    async def check(self, call: types.CallbackQuery) -> bool:
        return call.data == 'auto_payment'


class WalletFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '👛 Кошелек'


class ReportFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '📖 Отчет'


class Number(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if len(message.text.split()) == 1:
            if message.text.isdigit():
                return True
            else:
                await message.answer('Вы вели не верные данные. Введите заново целое число')
        elif len(message.text.split()) == 2:
            if message.text.split()[0].isdigit() and message.text.split()[1].isdigit():
                return True
            else:
                await message.answer('Вы вели не верные данные. Введите заново 2 числа (нал. безнал)')

        return False

