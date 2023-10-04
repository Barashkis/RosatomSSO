from datetime import datetime
from typing import Dict

from aiogram import types
from sqlalchemy import text

from rosatom_sso.config import (
    moderation_status,
    request_denied_status,
)
from rosatom_sso.database import CommonUser
from rosatom_sso.keyboards import (
    custom_cd,
    users_kb,
)
from rosatom_sso.loader import (
    PostgresSession,
    dp,
)
from rosatom_sso.logger import logger


@dp.callback_query_handler(custom_cd('inspect_common_users_single_pagination', keys=('page',)).filter(), state='*')
async def inspect_common_users_by_single_pagination(call: types.CallbackQuery, callback_data: Dict):
    page = int(callback_data['page'])
    logger.debug(f'Admin {call.from_user.id} enters inspect_common_users_by_single_pagination handler with {page=}')

    with PostgresSession.begin() as session:
        session.execute(text('SET timezone = \'Europe/Moscow\';'))
        if to_inspect := session.query(CommonUser).order_by(CommonUser.created_at.desc()).filter(
                CommonUser.status != request_denied_status,
                CommonUser.status != moderation_status,
        ).all():
            user: CommonUser = to_inspect[page - 1]
            username = '@' + user.username if user.username else 'не установлен'
            last_pressed_button = (
                last_pressed_button if (last_pressed_button := user.statistic.last_pressed_button)
                else 'нажатий не было'
            )
            await call.message.edit_text(
                f'Пользователей в системе: {len(to_inspect)}\n\n'
                '<i>Данные о пользователе</i>\n\n'
                f'<b>Имя в Telegram:</b> {username}\n'
                f'<b>Фамилия и имя:</b> {user.wr_fullname}\n'
                f'<b>Название отряда:</b> {user.squad_name}\n'
                f'<b>Статус:</b> {user.status}\n'
                f'<b>Количество баллов:</b> {user.points}\n'
                f'<b>Дата регистрации:</b> {datetime.strftime(user.created_at, "%d.%m.%Y, %H:%M:%S")} по МСК\n\n'
                '<i>Активность пользователя</i>\n\n'
                f'<b>Количество нажатых кнопок:</b> {user.statistic.presses}\n'
                f'<b>Название последней нажатой кнопки:</b> {last_pressed_button}\n'
                '<b>Последний раз был активен:</b> '
                f'{datetime.strftime(user.statistic.last_activity_date, "%d.%m.%Y, %H:%M:%S")} по МСК',
                reply_markup=users_kb(
                    scroll_callback_name='inspect_common_users_single_pagination',
                    back_callback_name='inspect_users',
                    total_pages=len(to_inspect),
                    page=page,
                )
            )
        else:
            await call.message.edit_text(
                'На данный момент тут пусто... Попробуйте зайти позже',
                reply_markup=call.message.reply_markup,
            )
