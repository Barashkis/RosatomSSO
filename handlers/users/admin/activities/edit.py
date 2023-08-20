import re
from datetime import datetime
from typing import Dict

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import quote_html

from config import tz
from database import Activity
from keyboards import (
    admin_main_menu_kb,
    custom_cd,
    edit_activity_kb,
)
from loader import (
    PostgresSession,
    dp,
)
from logger import logger

from ....exceptions import (
    WrongActivityPointsError,
    WrongAdminActivityIdError,
)


@dp.callback_query_handler(custom_cd('edit_activities').filter(), state='*')
async def list_activities_to_edit(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters list_activities_to_edit handler')

    with PostgresSession.begin() as session:
        if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).all():
            activities_text = '\n\n'.join(
                [
                    f'{i}. {a.name} '
                    f'(выполнение до {datetime.strftime(a.expires_at.astimezone(tz), "%d.%m")}) - {a.points} баллов'
                    for i, a in enumerate(activities, start=1)
                ]
            )
            await call.message.edit_reply_markup()
            await call.message.answer(
                'Список доступных для редактирования активностей. Чтобы выбрать активность, '
                'отправьте боту ее порядковый номер.\n\n' + activities_text,
            )
            await state.set_state('send_activity_to_edit_id')
        else:
            await call.message.edit_text(
                'На данный момент тут пусто... Попробуйте зайти позже',
                reply_markup=call.message.reply_markup,
            )


@dp.message_handler(state='send_activity_to_edit_id')
async def receive_activity_to_edit_id(message: types.Message, state: FSMContext):
    message_text = message.text
    logger.debug(f'Admin {message.from_user.id} enters receive_activity_to_edit_id handler with {message_text}')

    try:
        activity_id = int(message_text)
    except ValueError:
        raise WrongAdminActivityIdError(f'Activity id is not integer. The actual value is {message_text=}')

    with PostgresSession.begin() as session:
        if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).all():
            activities_count = len(activities)
            if 1 <= activity_id <= activities_count:
                activity = activities[activity_id - 1]
                await message.answer(
                    'Вы выбрали следующую активность:\n\n'
                    f'{activity.name} (выполнение до {datetime.strftime(activity.expires_at.astimezone(tz), "%d.%m")})'
                    f' - {activity.points} баллов',
                    reply_markup=edit_activity_kb(activity.id, is_actual=activity.is_actual),
                )
            else:
                raise WrongAdminActivityIdError(f'Activity id is not between 1 and {activities_count}')
        else:
            await message.answer(
                'На данный момент список активностей пуст',
                reply_markup=admin_main_menu_kb(),
            )
    await state.finish()


@dp.callback_query_handler(custom_cd('edit_activity_name', keys=('activity_id',)).filter(), state='*')
async def edit_activity_name(call: types.CallbackQuery, callback_data: Dict, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters edit_activity_name handler')

    await call.message.edit_reply_markup()
    await call.message.answer('Введите новое название активности')

    await state.set_state('send_new_activity_name')
    async with state.proxy() as data:
        data['activity_id'] = callback_data['activity_id']


@dp.message_handler(state='send_new_activity_name')
async def receive_new_activity_name(message: types.Message, state: FSMContext):
    new_activity_name = message.text
    logger.debug(f'Admin {message.from_user.id} enters receive_new_activity_name handler with {new_activity_name=}')

    with PostgresSession.begin() as session:
        async with state.proxy() as data:
            activity_id = data['activity_id']
            activity = session.get(Activity, activity_id)
            activity.name = new_activity_name

            await message.answer(
                'Название активности успешно обновлено.\n\n'
                f'{activity.name} (выполнение до '
                f'{datetime.strftime(activity.expires_at.astimezone(tz), "%d.%m")})'
                f' - {activity.points} баллов',
                reply_markup=edit_activity_kb(activity_id, is_actual=activity.is_actual),
            )
    await state.finish()


@dp.callback_query_handler(custom_cd('edit_activity_points', keys=('activity_id',)).filter(), state='*')
async def edit_activity_points(call: types.CallbackQuery, callback_data: Dict, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters edit_activity_points handler')

    await call.message.edit_reply_markup()
    await call.message.answer('Введите новое количество очков за активность')

    await state.set_state('send_new_activity_points')
    async with state.proxy() as data:
        data['activity_id'] = callback_data['activity_id']


@dp.message_handler(state='send_new_activity_points')
async def receive_activity_points(message: types.Message, state: FSMContext):
    logger.debug(f'Admin {message.from_user.id} enters receive_activity_points handler with {message.text=}')

    try:
        points = int(message.text)
    except ValueError:
        raise WrongActivityPointsError

    if points <= 0:
        raise WrongActivityPointsError

    with PostgresSession.begin() as session:
        async with state.proxy() as data:
            activity_id = data['activity_id']
            activity = session.get(Activity, activity_id)
            activity.points = points

            await message.answer(
                'Количество очков за активность успешно обновлено.\n\n'
                f'{activity.name} (выполнение до {datetime.strftime(activity.expires_at.astimezone(tz), "%d.%m")})'
                f' - {activity.points} баллов',
                reply_markup=edit_activity_kb(activity_id, is_actual=activity.is_actual),
            )
    await state.finish()


@dp.callback_query_handler(custom_cd('edit_activity_date', keys=('activity_id',)).filter(), state='*')
async def edit_activity_date(call: types.CallbackQuery, callback_data: Dict, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters edit_activity_date handler')

    await call.message.edit_reply_markup()
    await call.message.answer(
        quote_html(
            'Введите новую дату, до которой активность будет действительна, в формате <день>.<месяц>. Например, 31.08'
        ),
    )

    await state.set_state('send_new_activity_date')
    async with state.proxy() as data:
        data['activity_id'] = callback_data['activity_id']


@dp.message_handler(state='send_new_activity_date')
async def receive_activity_date(message: types.Message, state: FSMContext):
    date = message.text
    logger.debug(f'Admin {message.from_user.id} enters receive_activity_date handler with {date=}')

    if re.match(r'^(0?[1-9]|[12]\d|3[01])\.(0?[1-9]|1[0-2])$', date):
        day, month = date.split('.')
        with PostgresSession.begin() as session:
            async with state.proxy() as data:
                activity_id = data['activity_id']
                activity = session.get(Activity, activity_id)
                activity.expires_at = f'{datetime.now().astimezone(tz).year}-{month}-{day} 23:59:59+3'

            await message.answer(
                'Дата, до которой активность будет действительна, успешно обновлена.\n\n'
                f'{activity.name} (выполнение до {date})'
                f' - {activity.points} баллов',
                reply_markup=edit_activity_kb(activity_id, is_actual=activity.is_actual),
            )
            await state.finish()
    else:
        await message.answer('Отправленная Вами дата имеет неправильный формат. Повторите попытку еще раз')


@dp.callback_query_handler(custom_cd('edit_activity_relevance', keys=('activity_id',)).filter(), state='*')
async def edit_activity_relevance(call: types.CallbackQuery, callback_data: Dict,):
    logger.debug(f'Admin {call.from_user.id} enters edit_activity_relevance handler')

    with PostgresSession.begin() as session:
        activity_id = callback_data['activity_id']
        activity = session.get(Activity, activity_id)
        activity.is_actual = not activity.is_actual

        await call.message.edit_reply_markup(edit_activity_kb(activity_id, is_actual=activity.is_actual))
