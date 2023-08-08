from aiogram import types

from keyboards import (
    custom_cd,
    mailing_kb,
)
from loader import dp
from logger import logger


__all__ = (
    'dp',
)


@dp.callback_query_handler(custom_cd('mailing').filter(), state='*')
async def list_mailing_options(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters list_mailing_options handler')

    await call.message.edit_text(
        'Выберите желаемый тип рассылки',
        reply_markup=mailing_kb(),
    )
