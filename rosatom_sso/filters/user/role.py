from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from ...database import Admin
from ...loader import PostgresSession


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        with PostgresSession.begin() as session:
            user = session.query(Admin).get(message.from_user.id)
        return bool(user)
