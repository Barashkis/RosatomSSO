import logging
from datetime import (
    datetime,
    timezone,
)

from aiogram.types import Update
from aiogram.utils.exceptions import MessageNotModified

from ...database import Activity
from ...keyboards import (
    admin_main_menu_kb,
    common_user_main_menu_kb,
)
from ...loader import (
    PostgresSession,
    dp,
)
from ..exceptions import (
    ActivityPointsError,
    AdminActivityIdError,
    InputDateError,
    UserActivityIdError,
)


logger = logging.getLogger(__name__)


@dp.errors_handler()
async def catch_errors(update: Update, exception):
    if isinstance(exception, MessageNotModified):
        callback_query = update.callback_query
        logger.debug(f'User {callback_query.from_user.id} got an exception: {exception!r}')

        await callback_query.answer()
    elif isinstance(exception, UserActivityIdError):
        message = update.message
        logger.debug(f'User {message.from_user.id} got an exception: {exception!r}')

        with PostgresSession.begin() as session:
            if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).filter(
                    Activity.expires_at >= datetime.now(tz=timezone.utc),
                    Activity.is_actual,
            ).all():
                activities_text = '\n\n'.join(
                    [
                        f'{i}. {a.name} '
                        f'(выполнение до {datetime.strftime(a.expires_at.astimezone(), "%d.%m")})'
                        for i, a in enumerate(activities, start=1)
                    ]
                )
                await message.answer(
                    'Ты ввел неправильный номер активности... '
                    'Возможно, ты давно не заходил, и список активностей изменился, '
                    'поэтому вот актуальный список:\n\n' + activities_text + '\n\n'
                    'Выбери подходящий номер еще раз и отправь его',
                )
            else:
                await dp.current_state(user=message.from_user.id, chat=message.from_user.id).finish()
                await message.answer(
                    'Список активностей сейчас пуст... Возможно, ты давно не заходил, поэтому жди новых активностей!',
                    reply_markup=common_user_main_menu_kb(),
                )
    elif isinstance(exception, AdminActivityIdError):
        message = update.message
        logger.debug(f'Admin {message.from_user.id} got an exception: {exception!r}')

        with PostgresSession.begin() as session:
            if activities := session.query(Activity).order_by(Activity.expires_at, Activity.id).all():
                activities_text = '\n\n'.join(
                    [
                        f'{i}. {a.name} '
                        f'(выполнение до {datetime.strftime(a.expires_at.astimezone(), "%d.%m")})'
                        for i, a in enumerate(activities, start=1)
                    ]
                )
                await message.answer(
                    'Вы ввели неправильный номер активности... '
                    'Возможно, Вы давно не заходили, и список активностей изменился, '
                    'поэтому вот актуальный список:\n\n' + activities_text + '\n\n'
                    'Выберите подходящий номер еще раз и отправьте его',
                )
            else:
                await dp.current_state(user=message.from_user.id, chat=message.from_user.id).finish()
                await message.answer(
                    'Список активностей сейчас пуст... '
                    'Чтобы редактировать активности, необходимо, чтобы в списке была минимум одна',
                    reply_markup=admin_main_menu_kb(),
                )
    elif isinstance(exception, ActivityPointsError):
        message = update.message
        logger.debug(f'User {message.from_user.id} got an exception: {exception!r}')

        await message.answer('Вы ввели неправильное количество очков. Это должно быть положительно число')
    elif isinstance(exception, InputDateError):
        message = update.message
        logger.debug(f'User {message.from_user.id} got an exception: {exception!r}')

        await message.answer('Вы ввели несуществующую дату. Повторите попытку еще раз')
    else:
        logger.debug(f'User got an exception: {exception!r}')
