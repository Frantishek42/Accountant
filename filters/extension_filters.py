from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from database.accountant import RegisterUser
import keyboards.inline as nav
from logger.log import logger
from states.state_user import FSMUser
from aiogram.dispatcher import FSMContext


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


class UserPrivate(BoundFilter):
    """

    """
    async def check(self, message: types.Message) -> bool:
        logger.info(f'Идет проверка пользователя {message.from_user.first_name} на доступ кошелька')
        private = RegisterUser.get(RegisterUser.user_id == message.from_user.id)
        if private.private:
            return True
        await message.answer('Это функция не доступна 🛑 для Вас'
                             f'\n{message.from_user.first_name} Вы не оплатили 💸 доступ кошельку 👛')


class ProfitFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        print('profit')
        return message.text == '📈 Прибыль'


# class ExpensesAddFilter(BoundFilter):
#     async def check(self, message: types.Message) -> bool:
#         if len(message.text.split()) >= 1:
#         return message.text.isalpha()


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


async def get_user_id(state: FSMContext) -> int:
    async with state.proxy() as data:
        return data.get('user_id')
