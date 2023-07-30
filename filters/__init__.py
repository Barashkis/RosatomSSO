from aiogram import Dispatcher

from .message import (
    IsForwarded,
    IsFromUser,
)
from .user import IsAdmin


__all__ = (
    'IsAdmin',
    'IsFromUser',
    'IsForwarded',
    'setup',
)


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsForwarded)
    dp.filters_factory.bind(IsFromUser)
    dp.filters_factory.bind(IsAdmin)
