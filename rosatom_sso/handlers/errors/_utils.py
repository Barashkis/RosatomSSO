from datetime import (
    datetime,
    timezone,
)

from aiogram import types
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


__all__ = (
    'errors_mapping',
)


async def _activity_points_error_callback(message: types.Message) -> None:
    await message.answer('Вы ввели неправильное количество очков. Это должно быть положительно число')


async def _admin_activity_id_error_callback(message: types.Message) -> None:
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


async def _input_date_error_callback(message: types.Message) -> None:
    await message.answer('Вы ввели несуществующую дату. Повторите попытку еще раз')


async def _message_not_modified_callback(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer()


async def _user_activity_error_callback(message: types.Message) -> None:
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


errors_mapping = {
    ActivityPointsError: _activity_points_error_callback,
    AdminActivityIdError: _admin_activity_id_error_callback,
    InputDateError: _input_date_error_callback,
    MessageNotModified: _message_not_modified_callback,
    UserActivityIdError: _user_activity_error_callback,
}
