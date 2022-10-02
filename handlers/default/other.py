from aiogram.types import CallbackQuery
from logger.log import logger
from loader import dp, bot


@dp.callback_query_handler(lambda a: True, state='*')
async def get_other(call: CallbackQuery):
    print(call.data)
