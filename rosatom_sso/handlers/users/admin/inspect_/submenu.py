from aiogram import types

from rosatom_sso.keyboards import (
    custom_cd,
    inspect_users_kb,
)
from rosatom_sso.loader import dp
from rosatom_sso.logger import logger


__all__ = (
    'dp',
)


@dp.callback_query_handler(custom_cd('inspect_users').filter(), state='*')
async def inspect_users_submenu(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters inspect_users_submenu handler')

    await call.message.edit_text(
        'Выберите, как хотите просмотреть информацию о бойцах',
        reply_markup=inspect_users_kb(),
    )
