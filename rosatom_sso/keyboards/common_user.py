from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from .callback_data import custom_cd


def common_user_main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text='Активности',
            callback_data=custom_cd('available_activities').new(row=0, column=0),
        ),
        InlineKeyboardButton(
            text='Мои баллы',
            callback_data=custom_cd('my_points').new(row=1, column=0),
        ),
    )

    return kb


def cancel_choosing_activity_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data=custom_cd('cancel_choosing_activity').new(row=0, column=0),
        )
    )

    return kb
