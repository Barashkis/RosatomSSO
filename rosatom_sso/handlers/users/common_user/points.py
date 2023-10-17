import logging

from aiogram import types

from ....database import CommonUser
from ....keyboards import custom_cd
from ....loader import (
    PostgresSession,
    dp,
)


logger = logging.getLogger(__name__)


@dp.callback_query_handler(custom_cd('my_points').filter())
async def my_points(call: types.CallbackQuery):
    user_id = call.from_user.id
    logger.debug(f'User {user_id} enters my_points handler')

    with PostgresSession.begin() as session:
        points = session.get(CommonUser, user_id).points

    await call.message.edit_text(
        f'Заработанные баллы: {points}',
        reply_markup=call.message.reply_markup,
    )
