from aiogram import types

from rosatom_sso.database import CommonUser
from rosatom_sso.keyboards import custom_cd
from rosatom_sso.loader import (
    PostgresSession,
    dp,
)
from rosatom_sso.logger import logger


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
