from aiogram import Dispatcher
from .extension_filters import UserID


def setup(dp: Dispatcher):
    dp.filters_factory.bind(UserID)
