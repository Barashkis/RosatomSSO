from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from rosatom_sso.config import (
    moderation_status,
    request_denied_status,
)
from rosatom_sso.database import CommonUser
from rosatom_sso.keyboards import common_user_main_menu_kb
from rosatom_sso.loader import (
    PostgresSession,
    dp,
)
from rosatom_sso.logger import logger

from .._utils import update_state_data


@dp.message_handler(Command('start'))
async def start(message: types.Message, state: FSMContext):
    tg_user = message.from_user
    with PostgresSession.begin() as session:
        user_id = tg_user.id
        if user := session.get(CommonUser, user_id):
            if user.status == request_denied_status:
                await message.answer(
                    'К сожалению, модераторы не нашли тебя в списке участников. '
                    'Если ты уверен, что произошла ошибка, напиши нам в личные сообщения '
                    '<a href="https://vk.com/im?sel=-25236132">"Карьеры в Росатоме"</a>',
                )
                logger.debug(f'Denied in registration user {user_id} uses /start command')
            else:
                await message.answer(
                    'Ты уже зарегистрировался в боте. '
                    'Если ты хочешь получить доступ к главному меню, воспользуйся командой /menu'
                )
                logger.debug(f'Already registered user {user_id} uses /start command')
        else:
            await message.answer(
                'По мере прохождения профориентационной программы ты познакомишься с атомной отраслью '
                'и даже получишь возможность присоединиться к команде Росатома. '
                'Фиксируй свои активности, зарабатывай баллы и занимай верхние строчки '
                'в топе участников, чтобы получить призы от Росатома.\n\n'
                'Для начала давай познакомимся. Напиши, пожалуйста, имя и фамилию',
            )
            await update_state_data(
                state,
                'registration_data',
                id=user_id,
                username=tg_user.username,
                tg_firstname=tg_user.first_name,
                tg_lastname=tg_user.last_name,
            )
            await state.set_state('send_user_fullname')
            logger.debug(f'New user {user_id} starts the bot')


@dp.message_handler(Command('menu'))
async def menu(message: types.Message):
    user_id = message.from_user.id
    with PostgresSession.begin() as session:
        if user := session.query(CommonUser).filter(
                CommonUser.id == user_id,
                CommonUser.status != request_denied_status,
        ).first():
            if user.status == moderation_status:
                await message.answer(
                    'Ты не можешь использовать функционал бота, пока твоя анкета находится на модерации'
                )
                logger.debug(f'User on moderation {user_id} uses /menu command')
            else:
                await message.answer(
                    'Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu',
                    reply_markup=common_user_main_menu_kb(),
                )
                logger.debug(f'User {user_id} uses /menu command')
        else:
            await message.answer('Ты не зарегистрирован в боте. Чтобы зарегистрироваться, введи команду /start')
            logger.debug(f'Unregistered user {user_id} uses /menu command')


@dp.message_handler(Command('show_my_id'), state='*')
async def show_telegram_user_id(message: types.Message):
    await message.answer(message.from_user.id)
