import logging
from typing import Dict

from aiogram import types
from aiogram.dispatcher import FSMContext

from ....database import (
    CommonUser,
    Confirmation,
)
from ....keyboards import (
    admin_main_menu_kb,
    confirmations_kb,
    custom_cd,
)
from ....keyboards.admin import deny_confirmation_kb
from ....loader import (
    PostgresSession,
    bot,
    dp,
)


logger = logging.getLogger(__name__)


@dp.callback_query_handler(custom_cd('unchecked_confirmations', keys=('page',)).filter(), state='*')
async def unchecked_confirmations(call: types.CallbackQuery, callback_data: Dict):
    page = int(callback_data['page'])
    logger.debug(f'Admin {call.from_user.id} enters unchecked_confirmations handler with {page=}')

    with PostgresSession.begin() as session:
        if confirmations := session.query(Confirmation).filter_by(is_checked=False).all():
            confirmation: Confirmation = confirmations[page - 1]
            confirmation_file_type = confirmation.file.type
            if confirmation_file_type == 'photo':
                send_func = call.message.answer_photo
            elif confirmation_file_type == 'video':
                send_func = call.message.answer_video
            else:
                send_func = call.message.answer_document

            author = session.get(CommonUser, confirmation.user_id)
            done_some_activities_amount = len(
                [c for c in author.confirmations if c.is_checked and c.activity.name == confirmation.activity.name]
            )

            await call.message.edit_reply_markup()
            await send_func(
                confirmation.file_id,
                caption=f'<b>Автор:</b> {author.wr_fullname}\n'
                        f'<b>Название активности:</b> {confirmation.activity.name}\n'
                        '<b>Количество одобренных активностей данного типа этому пользователю:</b> '
                        f'{done_some_activities_amount}\n'
                        f'<b>Комментарий:</b> '
                        f'{caption if (caption := confirmation.file.caption) is not None else "отсутствует"}',
                reply_markup=confirmations_kb(
                    scroll_callback_name='unchecked_confirmations',
                    back_callback_name='new_admin_menu',
                    total_pages=len(confirmations),
                    page=page,
                    confirmation_id=confirmation.id,
                    user_id=confirmation.user_id,
                ),
            )
        else:
            await call.message.edit_text(
                'На данный момент тут пусто... Попробуйте зайти позже',
                reply_markup=call.message.reply_markup,
            )


@dp.callback_query_handler(custom_cd('approve_confirmation', keys=('user_id', 'confirmation_id')).filter(), state='*')
async def approve_confirmation(call: types.CallbackQuery, callback_data: Dict):
    confirmation_id = int(callback_data['confirmation_id'])
    logger.debug(f'Admin {call.from_user.id} enters approve_confirmation handler with {confirmation_id=}')

    with PostgresSession.begin() as session:
        confirmation = session.get(Confirmation, confirmation_id)
        confirmation.is_checked = True

        activity = confirmation.activity
        user = confirmation.user
        user.points += activity.points
        user.status = f'Получил {activity.points} баллов за активность {activity.name!r}'

        await bot.send_message(
            int(callback_data['user_id']),
            f'Поздравляем! {activity.points} баллов за активность {activity.name!r} добавлены к твоему рейтингу'
        )

    await call.message.edit_reply_markup()
    await call.message.answer(
        'Активность была успешно одобрена',
        reply_markup=admin_main_menu_kb(),
    )


@dp.callback_query_handler(custom_cd('deny_confirmation', keys=('user_id', 'confirmation_id')).filter(), state='*')
async def deny_confirmation(call: types.CallbackQuery, callback_data: Dict):
    confirmation_id = int(callback_data['confirmation_id'])
    activity_user_id = int(callback_data['user_id'])
    logger.debug(
        f'Admin {call.from_user.id} enters deny_confirmation '
        f'handler with {confirmation_id=} of user {activity_user_id}'
    )

    await call.message.edit_reply_markup()
    await call.message.answer(
        'Выберите нужный вариант отклонения активности',
        reply_markup=deny_confirmation_kb(activity_user_id, confirmation_id),
    )


@dp.callback_query_handler(
    custom_cd(
        'deny_confirmation_without_comment',
        keys=('user_id', 'confirmation_id')
    ).filter(),
    state='*'
)
async def deny_confirmation_without_comment(call: types.CallbackQuery, callback_data: Dict):
    confirmation_id = int(callback_data['confirmation_id'])
    activity_user_id = int(callback_data['user_id'])
    logger.debug(
        f'Admin {call.from_user.id} enters deny_confirmation_without_comment '
        f'handler with {confirmation_id=} of user {activity_user_id}'
    )

    with PostgresSession.begin() as session:
        confirmation = session.get(Confirmation, confirmation_id)
        confirmation.is_checked = True

        activity = confirmation.activity
        confirmation.user.status = f'Получил отказ в выполнении активности {activity.name!r}'

        await bot.send_message(
            activity_user_id,
            f'К сожалению, твое выполнение активности {activity.name!r} было отклонено...'
        )

    await call.message.edit_reply_markup()
    await call.message.answer(
        'Активность была успешно отклонена',
        reply_markup=admin_main_menu_kb(),
    )


@dp.callback_query_handler(
    custom_cd(
        'deny_confirmation_with_comment',
        keys=('user_id', 'confirmation_id')
    ).filter(),
    state='*'
)
async def deny_confirmation_with_comment(call: types.CallbackQuery, state: FSMContext, callback_data: Dict):
    confirmation_id = int(callback_data['confirmation_id'])
    activity_user_id = int(callback_data['user_id'])
    logger.debug(
        f'Admin {call.from_user.id} enters deny_confirmation_with_comment '
        f'handler with {confirmation_id=} of user {activity_user_id}'
    )

    async with state.proxy() as data:
        data['activity_user_id'] = activity_user_id
        data['confirmation_id'] = confirmation_id

    await call.message.edit_reply_markup()
    await call.message.answer('Напишите комментарий')
    await state.set_state('send_deny_activity_comment')


@dp.message_handler(state='send_deny_activity_comment')
async def receive_deny_activity_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        activity_user_id = data['activity_user_id']
        confirmation_id = data['confirmation_id']
    logger.debug(
        f'Admin {message.from_user.id} enters receive_deny_activity_comment '
        f'handler with {confirmation_id=} of user {activity_user_id}'
    )

    with PostgresSession.begin() as session:
        confirmation = session.get(Confirmation, confirmation_id)
        confirmation.is_checked = True

        activity = confirmation.activity
        confirmation.user.status = f'Получил отказ в выполнении активности {activity.name!r}'

        await bot.send_message(
            activity_user_id,
            f'К сожалению, твое выполнение активности {activity.name!r} было отклонено...\n\n'
            '<i>Комментарий от модератора:</i>\n\n'
            f'{message.text}',
        )

    await message.answer(
        'Активность была успешно отклонена',
        reply_markup=admin_main_menu_kb(),
    )
    await state.finish()


@dp.callback_query_handler(custom_cd('new_admin_menu').filter(), state='*')
async def admin_menu(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters admin_menu handler')

    text = (
        'Добро пожаловать в панель администратора! Здесь Вы можете просматривать заявки от пользователей, '
        'информацию о прошедших регистрацию пользователях, редактировать, а также создавать активности и подарки'
    )
    await call.message.edit_reply_markup()
    await call.message.answer(text, reply_markup=admin_main_menu_kb())
