from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


__all__ = (
    'IsForwarded',
    'IsFromUser',
)


class IsForwarded(BoundFilter):
    async def check(self, message: types.Message):
        return message.is_forward()


class IsFromUser(BoundFilter):
    async def check(self, message: types.Message):
        return message.forward_from.is_bot
