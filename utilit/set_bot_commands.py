from aiogram import types


async def set_default_commands(dp):
    """
    Функция для появления в меню команд по умолчанию

    :param dp:
    :return:
    """
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустить бота'),
            types.BotCommand('help', 'Помощь'),
            types.BotCommand('join', 'Объединить пользователей'),
        ]
    )
