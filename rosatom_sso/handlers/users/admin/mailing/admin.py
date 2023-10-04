import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from rosatom_sso.database import Admin
from rosatom_sso.keyboards import (
    custom_cd,
    mailing_kb,
)
from rosatom_sso.loader import (
    PostgresSession,
    dp,
)
from rosatom_sso.logger import logger

from ...._utils import send_message


@dp.callback_query_handler(custom_cd('mailing_all_admins').filter(), state='*')
async def mailing_all_admins(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters mailing_all_admins handler')

    await call.message.edit_reply_markup()
    await call.message.answer(
        'Отправьте сообщение, которые хотите разослать всем модераторам. '
        'Если Вы хотите выйти из режима рассылки, пришлите боту '
        'сообщение "Назад" (без кавычек)',
    )
    await state.set_state('send_message_to_all_admins')


@dp.message_handler(
    state='send_message_to_all_admins',
    content_types=[ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO, ContentType.TEXT],
)
async def receive_message_to_all_admins(message: types.Message, state: FSMContext):
    logger.debug(f'Admin {message.from_user.id} enters receive_message_to_all_admins handler')

    if (content_type := str(message.content_type)) == 'text':
        message_text = message.text
        if message_text.lower() == 'назад':
            await message.answer('Процесс рассылки модераторам был отменен', reply_markup=mailing_kb())

    with PostgresSession.begin() as session:
        for moderator in session.query(Admin).all():
            await send_message(chat_id=moderator.id, content_type=content_type, message=message)
            await asyncio.sleep(.05)

    await message.answer(
        'Ваше сообщение было успешно разослано всем активным модераторам',
        reply_markup=mailing_kb(),
    )

    await state.finish()
