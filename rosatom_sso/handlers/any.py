from aiogram import types
from aiogram.types import ContentType

from rosatom_sso.loader import dp
from rosatom_sso.logger import logger


@dp.message_handler(content_types=ContentType.ANY, state='*')
async def other_messages(message: types.Message):
    logger.debug(f'User {message.from_user.id} enters other_messages with message type {message.content_type!r}')

    await message.answer(
        'К сожалению, я не знаю, как ответить на это сообщение...\n\n'
        'Чтобы взаимодействовать с ботом, необходимо использовать меню или команды',
    )


@dp.callback_query_handler(state='*')
async def other_callback_queries(call: types.Message):
    logger.debug(f'User {call.from_user.id} enters other_callback_queries')

    await call.answer('В данный момент эта опция не доступна')
