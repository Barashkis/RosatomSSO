from aiogram import Dispatcher

from .user import IsAdmin


__all__ = (
    'IsAdmin',
    'setup',
)


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsAdmin)
