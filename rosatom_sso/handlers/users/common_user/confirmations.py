from datetime import (
    datetime,
    timezone,
)

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from ....database import (
    Activity,
    CommonUser,
    Confirmation,
    File,
)
from ....keyboards import (
    cancel_choosing_activity_kb,
    common_user_main_menu_kb,
    custom_cd,
)
from ....loader import (
    PostgresSession,
    dp,
)
from ....logger import logger
from ....utils import message_file_utils_dict
from ...exceptions import UserActivityIdError


@dp.callback_query_handler(custom_cd('available_activities').filter())
async def available_activities(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'User {call.from_user.id} enters available_activities handler')

    with PostgresSession.begin() as session:
        if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).filter(
                Activity.expires_at >= datetime.now(tz=timezone.utc),
                Activity.is_actual
        ).all():
            activities_text = '\n\n'.join(
                [
                    f'{i}. {a.name} (выполнение до {datetime.strftime(a.expires_at.astimezone(), "%d.%m")})'
                    for i, a in enumerate(activities, start=1)
                ]
            )
            await call.message.edit_reply_markup()
            await call.message.answer(
                'Вот список активностей, в которых ты можешь принять участие. '
                'Если ты хочешь зафиксировать выполнение, пришли в чат цифру, которая соответствует действию.\n\n'
                'Список активностей:\n\n' + activities_text,
                reply_markup=cancel_choosing_activity_kb(),
            )
            await state.set_state('init_confirmation')
        else:
            await call.message.edit_text(
                'В системе пока нету никаких активностей... Попробуй зайти позже',
                reply_markup=call.message.reply_markup,
            )


@dp.callback_query_handler(custom_cd('cancel_choosing_activity').filter(), state='*')
async def cancel_choosing_activity(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'User {call.from_user.id} enters cancel_choosing_activity handler')

    if await state.get_state() == 'init_confirmation':
        await call.message.edit_text(
            'Ты в главном меню. Если захочешь вернуться сюда, воспользуйся командой /menu',
            reply_markup=common_user_main_menu_kb(),
        )
        await state.finish()
    else:
        await call.message.edit_text(
            'Ты уже начал процесс фиксации выполнения активности. '
            'Чтобы получить доступ к меню, надо его завершить.\n\n' + call.message.text,
        )


@dp.message_handler(state='init_confirmation')
async def receive_activity_id(message: types.Message, state: FSMContext):
    message_text = message.text
    logger.debug(f'User {message.from_user.id} enters receive_activity_id handler with {message_text=}')

    try:
        activity_id = int(message_text)
    except ValueError:
        raise UserActivityIdError(f'Activity id is not integer. The actual value is {message_text=}')

    with PostgresSession.begin() as session:
        if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).filter(
                Activity.expires_at >= datetime.now(tz=timezone.utc),
                Activity.is_actual,
        ).all():
            activities_count = len(activities)
            if 1 <= activity_id <= activities_count:
                activity = activities[activity_id - 1]
                await message.answer(
                    f'Отлично! Ты выбрал активность {activity.name!r}.\n\n'
                    'Пришли в чат сообщение, подтверждающее выполнение действия. '
                    'Это может быть фотография с мероприятия, скриншот просмотренного видео и так далее. '
                    'Тип файла может быть одним из следующих:\n\n'
                    '1. Фото\n'
                    '2. Документ\n'
                    '3. Видео\n\n'
                    'Также не забудь написать текстовое сообщение к этому файлу. '
                    'Текст нужно отправлять вместе с файлом (в одном сообщении)',
                )

                await state.set_state('send_confirmation')
                await state.update_data({'activity_id': activity.id})
            else:
                raise UserActivityIdError(f'Activity id is not between 1 and {activities_count}')
        else:
            await message.answer(
                'На данный момент список активностей пуст',
                reply_markup=common_user_main_menu_kb(),
            )
            await state.finish()


@dp.message_handler(
    state='send_confirmation',
    content_types=[ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO],
)
async def receive_confirmation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    content_type = str(message.content_type)
    caption = message.caption
    logger.debug(f'User {user_id} enters receive_confirmation handler with {content_type=} and {caption=}')

    with PostgresSession.begin() as session:
        async with state.proxy() as data:
            activity_id = data['activity_id']

        file_id = message_file_utils_dict[content_type].file_id(message)
        file = File(id=file_id, caption=caption, type=content_type)
        session.add(Confirmation(user_id=user_id, activity_id=activity_id, file=file))

        activity = session.get(Activity, activity_id)
        session.query(CommonUser).filter_by(id=user_id).update(
            {
                'status': f'Зафиксировал активность {activity.name!r}'
            }
        )

    await message.answer(
        'Отлично! Теперь дело за модераторами. Они проверят твой ответ и примут решение, засчитывать его или нет. '
        'Когда проверка закончится, тебе придет уведомление',
        reply_markup=common_user_main_menu_kb(),
    )
    await state.finish()


@dp.message_handler(state='send_confirmation')
async def incorrect_confirmation_content_type(message: types.Message):
    logger.debug(f'User {message.from_user.id} enters incorrect_file_content_type handler')

    await message.answer(
        'Тип сообщения может быть одним из следующих:\n\n'
        '1. Фото\n'
        '2. Документ\n'
        '3. Видео\n\n'
        'Повтори попытку еще раз',
    )
