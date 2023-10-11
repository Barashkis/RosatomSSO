from aiogram import types

from .....keyboards import (
    custom_cd,
    moderate_activities_kb,
)
from .....loader import dp
from .....logger import logger


@dp.callback_query_handler(custom_cd('moderate_activities').filter(), state='*')
async def list_actions_with_activities(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters list_actions_with_activities handler')

    await call.message.edit_text(
        'Выберите желаемое действие с активностями',
        reply_markup=moderate_activities_kb(),
    )
