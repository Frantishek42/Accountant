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


class Profit(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '📈 Прибыль'


class Expenses(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '📉 Затраты'


class Wallet(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '👛 Кошелек'


class Report(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text == '📖 Отчет'


class Number(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if message.text.isdigit():
            return True
        else:
            await message.answer('Вы вели не верные данные. Введите заново целое число')
            return False
