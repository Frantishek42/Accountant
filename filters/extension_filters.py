from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class UserID(BoundFilter):
    """
    Дочерний класс UserID родитель BoundFilter создан для фильтрации id пользователя

    """
    async def check(self, message: types.Message) -> bool:
        """
        Функция для проверки id пользователя
        :param message:
        :return:
        """
        return message.from_user.id in [49577767, 1362130241]


class ProfitFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '📈 Прибыль'


class ExpensesFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '📉 Затраты'


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
        elif len(message.text.split()) == 2:
            if message.text.split()[0].isdigit() and message.text.split()[1].isdigit():
                return True
        await message.answer('Вы вели не верные данные. Введите заново целое число')
        return False
