from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from ._utils import pagination
from .callback_data import custom_cd


def admin_main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Пользователи',
            callback_data=custom_cd('inspect_users', keys=('page',)).new(page=1, row=0, column=0),
        ),
        InlineKeyboardButton(
            text='Новые анкеты',
            callback_data=custom_cd('moderate_requests', keys=('page',)).new(page=1, row=1, column=0),
        ),
        InlineKeyboardButton(
            text='Отклоненные анкеты',
            callback_data=custom_cd('denied_requests', keys=('page',)).new(page=1, row=2, column=0),
        ),
        InlineKeyboardButton(
            text='Непроверенные активности',
            callback_data=custom_cd('unchecked_confirmations', keys=('page',)).new(page=1, row=3, column=0),
        ),
        InlineKeyboardButton(
            text='Активности (модерация)',
            callback_data=custom_cd('moderate_activities').new(row=4, column=0),
        ),
        InlineKeyboardButton(
            text='Добавить модератора',
            callback_data=custom_cd('add_moderator').new(row=5, column=0),
        ),
        InlineKeyboardButton(
            text='Рассылка',
            callback_data=custom_cd('mailing').new(row=6, column=0),
        ),
    )

    return kb


@pagination
def confirmations_kb(user_id: int, confirmation_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Одобрить',
            callback_data=custom_cd('approve_confirmation', keys=('user_id', 'confirmation_id',)).new(
                user_id=user_id,
                confirmation_id=confirmation_id,
                row=0,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Отклонить',
            callback_data=custom_cd('deny_confirmation', keys=('user_id', 'confirmation_id',)).new(
                user_id=user_id,
                confirmation_id=confirmation_id,
                row=1,
                column=0,
            )
        ),
    )

    return kb


def edit_activity_kb(activity_id: int, is_actual: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Название',
            callback_data=custom_cd('edit_activity_name', keys=('activity_id',)).new(
                activity_id=activity_id,
                row=0,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Количество баллов',
            callback_data=custom_cd('edit_activity_points', keys=('activity_id',)).new(
                activity_id=activity_id,
                row=1,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Действительна до',
            callback_data=custom_cd('edit_activity_date', keys=('activity_id',)).new(
                activity_id=activity_id,
                row=2,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text=f'Сделать{" не " if is_actual else " "}активной',
            callback_data=custom_cd('edit_activity_relevance', keys=('activity_id',)).new(
                activity_id=activity_id,
                row=3,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Назад',
            callback_data=custom_cd('moderate_activities').new(
                row=4,
                column=0,
            )
        ),
    )

    return kb


def mailing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Всем бойцам ССО',
            callback_data=custom_cd('mailing_all_moderators').new(
                row=0,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Всем модераторам',
            callback_data=custom_cd('mailing_all_common_users').new(
                row=1,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Назад',
            callback_data=custom_cd('admin_menu').new(
                row=2,
                column=0,
            )
        ),
    )

    return kb


def moderate_activities_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Список действующих активностей',
            callback_data=custom_cd('actual_activities').new(
                row=0,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Создать',
            callback_data=custom_cd('create_activity').new(
                row=1,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Редактировать',
            callback_data=custom_cd('edit_activities').new(
                row=2,
                column=0,
            )
        ),
        InlineKeyboardButton(
            text='Назад',
            callback_data=custom_cd('admin_menu').new(
                row=3,
                column=0,
            )
        ),
    )

    return kb


@pagination
def recover_request_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Восстановить',
            callback_data=custom_cd('recover_user', keys=('user_id',)).new(user_id=user_id, row=0, column=0)
        ),
    )

    return kb


@pagination
def requests_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Одобрить',
            callback_data=custom_cd('approve_request', keys=('user_id',)).new(user_id=user_id, row=0, column=0)
        ),
        InlineKeyboardButton(
            text='Отклонить',
            callback_data=custom_cd('deny_request', keys=('user_id',)).new(user_id=user_id, row=1, column=0)
        ),
    )

    return kb


@pagination
def users_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup()
