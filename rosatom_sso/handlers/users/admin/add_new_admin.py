from aiogram import types
from aiogram.dispatcher import FSMContext

from rosatom_sso.database import Admin
from rosatom_sso.keyboards import (
    admin_main_menu_kb,
    custom_cd,
)
from rosatom_sso.loader import (
    PostgresSession,
    dp,
)
from rosatom_sso.logger import logger


async def add_new_admin(new_admin_id: int, message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    with PostgresSession.begin() as session:
        admin_ids = [admin.id for admin in session.query(Admin).all()]
        if new_admin_id not in admin_ids:
            session.add(Admin(id=new_admin_id))

            logger.debug(f'Admin {user_id} enters receive_message_from_new_admin with {new_admin_id=}')
            await message.answer(
                'Пользователь был добавлен в список модераторов бота',
                reply_markup=admin_main_menu_kb(),
            )
            await state.finish()
        else:
            logger.debug(
                f'Admin {user_id} enters receive_message_from_new_admin with '
                f'message from already registered admin with {new_admin_id=}'
            )
            await message.answer(
                'Данный пользователь уже является модератором. Выберите, пожалуйста, другого пользователя',
            )


@dp.callback_query_handler(custom_cd('add_admin').filter(), state='*')
async def add_admin(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters add_admin')

    await call.message.edit_reply_markup()
    await call.message.answer(
        'Перешлите в бота любое сообщение пользователя, которого хотите сделать модератором. '
        'Если его профиль закрыт, пришлите сообщение с его ID. Для этого попросите его воспользоваться командой '
        '/show_my_id и передать идентификатор Вам (сообщение с ID можно как прислать самому, '
        'так и переслать напрямую). Также, если Вы хотите выйти из режима добавления нового модератора, пришлите боту '
        'сообщение "Назад" (без кавычек)'
    )

    await state.set_state('send_message_from_new_admin')


@dp.message_handler(content_types=types.ContentType.ANY, state='send_message_from_new_admin')
async def receive_message_from_new_admin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if new_admin := message.forward_from:
        if new_admin.is_bot:
            logger.debug(f'Admin {user_id} enters receive_message_from_new_admin with message from bot')
            await message.answer(
                'Сообщение должно принадлежать человеку, а не боту. Повторите попытку еще раз',
            )
        else:
            await add_new_admin(new_admin.id, message, state)
    elif (message_text := message.text).isdigit():
        await add_new_admin(int(message_text), message, state)
    elif message_text == 'Назад':
        await message.answer('Процесс добавления нового модератора был отменен', reply_markup=admin_main_menu_kb())
        await state.finish()
    else:
        logger.debug(f'Admin {user_id} enters receive_message_from_new_admin with not forwarded message')
        await message.answer(
            'Необходимо переслать сообщение другого пользователя либо прислать его числовой идентификатор. '
            'Повторите попытку еще раз',
        )
