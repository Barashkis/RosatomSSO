import logging
import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import quote_html

from .....config import TIMEZONE
from .....database import Activity
from .....keyboards import (
    custom_cd,
    moderate_activities_kb,
)
from .....loader import (
    PostgresSession,
    dp,
)
from ...._utils import update_state_data
from ....exceptions import (
    ActivityPointsError,
    InputDateError,
)


logger = logging.getLogger(__name__)


@dp.callback_query_handler(custom_cd('create_activity').filter(), state='*')
async def create_activity(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters create_activity handler')

    await call.message.edit_reply_markup()
    await call.message.answer('Введите название создаваемой активности')
    await state.set_state('send_activity_name')


@dp.message_handler(state='send_activity_name')
async def receive_activity_name(message: types.Message, state: FSMContext):
    activity_name = message.text
    logger.debug(f'Admin {message.from_user.id} enters receive_activity_name handler with {activity_name=}')

    await update_state_data(state, 'activity_data', name=activity_name)
    await message.answer('Напишите количество очков за данную активность')

    await state.set_state('send_activity_points')


@dp.message_handler(state='send_activity_points')
async def receive_activity_points(message: types.Message, state: FSMContext):
    logger.debug(f'Admin {message.from_user.id} enters receive_activity_points handler with with {message.text=}')

    try:
        points = int(message.text)
    except ValueError:
        raise ActivityPointsError

    if points <= 0:
        raise ActivityPointsError

    await update_state_data(state, 'activity_data', points=points)
    await message.answer(
        quote_html(
            'Напишите, до какой даты действительна данная активность, в формате <день>.<месяц>. Например, 31.08'
        ),
    )

    await state.set_state('send_activity_expiration_date')


@dp.message_handler(state='send_activity_expiration_date')
async def receive_activity_expiration_date(message: types.Message, state: FSMContext):
    date = message.text
    logger.debug(f'Admin {message.from_user.id} enters receive_activity_expiration_date handler with {date=}')

    if re.match(r'^(0?[1-9]|[12]\d|3[01])\.(0?[1-9]|1[0-2])$', date):
        day, month = [int(date_element) for date_element in date.split('.')]
        year = datetime.now().astimezone(TIMEZONE).year
        try:
            dt = datetime(year, month, day, 23, 59, 59, tzinfo=TIMEZONE)
        except ValueError:
            raise InputDateError

        with PostgresSession.begin() as session:
            async with state.proxy() as data:
                session.add(Activity(**data['activity_data'], expires_at=dt))

        await state.reset_data()
        await message.answer('Активность была успешно добавлена', reply_markup=moderate_activities_kb())
    else:
        await message.answer('Отправленная Вами дата имеет неправильный формат. Повторите попытку еще раз')
