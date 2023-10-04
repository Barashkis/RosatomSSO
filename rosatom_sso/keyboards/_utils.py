from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from .callback_data import custom_cd


def pagination(func):
    def wrapper(
            scroll_callback_name: str,
            back_callback_name: str,
            total_pages: int,
            page: int = 1,
            *args,
            **kwargs,
    ) -> InlineKeyboardMarkup:
        kb: InlineKeyboardMarkup = func(*args, **kwargs)
        row = len(kb.inline_keyboard)
        if page != 0:
            scroll_row = []
            column = 0
            if page > 1:
                scroll_row.append(
                    InlineKeyboardButton(
                        text='⏮',
                        callback_data=custom_cd(scroll_callback_name, keys=('page',)).new(
                            page=page - 1,
                            row=row,
                            column=column,
                        )
                    )
                )
                column += 1
            if page < total_pages:
                scroll_row.append(
                    InlineKeyboardButton(
                        text='⏭',
                        callback_data=custom_cd(scroll_callback_name, keys=('page',)).new(
                            page=page + 1,
                            row=row,
                            column=column,
                        )
                    )
                )
            if scroll_row:
                kb.row(*scroll_row)
                row += 1
        kb.row(
            InlineKeyboardButton(
                text='Назад',
                callback_data=custom_cd(back_callback_name).new(
                    row=row,
                    column=0,
                )
            )
        )

        return kb

    return wrapper
