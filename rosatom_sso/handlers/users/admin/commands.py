from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import Command

from ....filters import IsAdmin
from ....keyboards import (
    admin_main_menu_kb,
    custom_cd,
)
from ....loader import dp
from ....logger import logger


@dp.message_handler(IsAdmin(), Command('admin_menu'), state='*')
@dp.callback_query_handler(custom_cd('admin_menu').filter(), state='*')
async def admin_menu(update: Union[types.Message, types.CallbackQuery]):
    logger.debug(f'Admin {update.from_user.id} enters admin_menu handler')

    text = (
        'Добро пожаловать в панель администратора! Здесь Вы можете просматривать заявки от пользователей, '
        'информацию о прошедших регистрацию пользователях, редактировать, а также создавать активности и подарки'
    )
    answer = update.answer if isinstance(update, types.Message) else update.message.edit_text
    await answer(text, reply_markup=admin_main_menu_kb())
