from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from ....config import MODERATION_STATUS
from ....database import CommonUser
from ....loader import (
    PostgresSession,
    dp,
)
from ....logger import logger
from ..._utils import update_state_data


@dp.message_handler(state='send_user_fullname')
async def receive_user_fullname(message: types.Message, state: FSMContext):
    logger.debug(f'User {message.from_user.id} enters receive_user_fullname handler')

    await update_state_data(state, 'registration_data', wr_fullname=message.text)
    await message.answer('Отлично. Теперь напиши, как называется твой отряд')

    await state.set_state('send_user_squad_name')


@dp.message_handler(state='send_user_squad_name')
async def receive_user_squad_name(message: types.Message, state: FSMContext):
    logger.debug(f'User {message.from_user.id} enters receive_user_squad_name handler')

    await update_state_data(state, 'registration_data', squad_name=message.text)
    with PostgresSession.begin() as session:
        async with state.proxy() as data:
            user = CommonUser(**data['registration_data'], status=MODERATION_STATUS)
            session.add(user)
    await state.reset_data()
    await message.answer('Модераторы скоро проверят твою заявку на присоединение к чат-боту. Ты получишь уведомление')

    await state.set_state('on_moderation')


@dp.message_handler(state='on_moderation', content_types=ContentType.ANY)
async def on_moderation(message: types.Message):
    logger.debug(
        f'User {message.from_user.id} sends message with type {message.content_type!r} being on moderation'
    )
    await message.answer(
        'Твоя заявка на присоединение к чат-боту находится на рассмотрении у модераторов. '
        'Ты получишь уведомление, когда ее рассмотрят'
    )
