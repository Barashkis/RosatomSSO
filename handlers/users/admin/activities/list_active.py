from datetime import (
    datetime,
    timezone,
)

from aiogram import types

from config import tz
from database import Activity
from keyboards import custom_cd
from loader import (
    PostgresSession,
    dp,
)
from logger import logger


@dp.callback_query_handler(custom_cd('actual_activities').filter(), state='*')
async def list_actual_activities(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters list_actual_activities handler')

    with PostgresSession.begin() as session:
        if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).filter(
                Activity.expires_at >= datetime.now(tz=timezone.utc),
                Activity.is_actual,
        ).all():
            message_text = '\n\n'.join(
                [
                    f'{i}. {a.name} '
                    f'(выполнение до {datetime.strftime(a.expires_at.astimezone(tz), "%d.%m")}) - {a.points} баллов'
                    for i, a in enumerate(activities, start=1)
                ]
            )
        else:
            message_text = 'На данный момент тут пусто... Попробуйте зайти позже'

    await call.message.edit_text(message_text, reply_markup=call.message.reply_markup)
