import logging

from aiogram import types

from .....keyboards import (
    custom_cd,
    requests_kb,
)
from .....loader import dp


logger = logging.getLogger(__name__)


__all__ = (
    'dp',
)


@dp.callback_query_handler(custom_cd('requests').filter(), state='*')
async def list_requests_types(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters list_mailing_options handler')

    await call.message.edit_text(
        'Выберите желаемый тип анкет',
        reply_markup=requests_kb(),
    )
