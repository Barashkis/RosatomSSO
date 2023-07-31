from aiogram import types
from aiogram.dispatcher import FSMContext

from database import Admin
from keyboards import (
    admin_main_menu_kb,
    custom_cd,
)
from loader import (
    PostgresSession,
    dp,
)
from logger import logger


@dp.callback_query_handler(custom_cd('add_moderator').filter(), state='*')
async def add_moderator(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters add_moderator')

    await call.message.edit_reply_markup()
    await call.message.answer('Перешлите в бота любое сообщение пользователя, которого хотите сделать модератором')

    await state.set_state('send_message_from_new_moderator')


@dp.message_handler(state='send_message_from_new_moderator')
async def receive_message_from_new_moderator(message: types.Message, state: FSMContext):
    new_admin = message.forward_from.id
    logger.debug(f'Admin {message.from_user.id} enters receive_message_from_new_moderator with {new_admin=}')

    with PostgresSession.begin() as session:
        session.add(Admin(id=new_admin))

    await message.answer(
        'Пользователь был добавлен в список модераторов бота',
        reply_markup=admin_main_menu_kb(),
    )
    await state.finish()
