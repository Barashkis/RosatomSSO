from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

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


@dp.message_handler(content_types=ContentType.ANY, state='send_message_from_new_moderator')
async def receive_message_from_new_moderator(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message_from_new_admin := message.forward_from:
        if message_from_new_admin.is_bot:
            logger.debug(f'Admin {user_id} enters receive_message_from_new_moderator with message from bot')
            await message.answer(
                'Сообщение должно принадлежать человеку, а не боту. Повторите попытку еще раз',
            )
        else:
            new_admin_id = message_from_new_admin.id
            logger.debug(f'Admin {user_id} enters receive_message_from_new_moderator with {new_admin_id=}')

            with PostgresSession.begin() as session:
                admin_ids = [admin.id for admin in session.query(Admin).all()]
                if new_admin_id not in admin_ids:
                    session.add(Admin(id=new_admin_id))

                    await message.answer(
                        'Пользователь был добавлен в список модераторов бота',
                        reply_markup=admin_main_menu_kb(),
                    )
                    await state.finish()
                else:
                    logger.debug(
                        f'Admin {user_id} enters receive_message_from_new_moderator with '
                        f'message from already registered admin with {new_admin_id=}'
                    )
                    await message.answer(
                        'Данный пользователь уже является модератором. Выберите, пожалуйста, другого пользователя',
                    )
    else:
        logger.debug(f'Admin {user_id} enters receive_message_from_new_moderator with not forwarded message')
        await message.answer(
            'Необходимо переслать сообщение другого пользователя. Повторите попытку еще раз',
        )
