import logging
from typing import Dict

from aiogram import types

from .....config import REQUEST_DENIED_STATUS
from .....database import CommonUser
from .....keyboards import (
    admin_main_menu_kb,
    custom_cd,
    recover_request_kb,
)
from .....loader import (
    PostgresSession,
    bot,
    dp,
)


logger = logging.getLogger(__name__)


@dp.callback_query_handler(custom_cd('denied_requests', keys=('page',)).filter(), state='*')
async def recover_requests(call: types.CallbackQuery, callback_data: Dict):
    page = int(callback_data['page'])
    logger.debug(f'Admin {call.from_user.id} enters recover_requests handler with {page=}')

    with PostgresSession.begin() as session:
        if to_recover := session.query(CommonUser).filter_by(status=REQUEST_DENIED_STATUS).all():
            user: CommonUser = to_recover[page - 1]
            username = '@' + user.username if user.username else 'не установлен'
            await call.message.edit_text(
                f'<b>Имя в Telegram:</b> {username}\n'
                f'<b>Фамилия и имя:</b> {user.wr_fullname}\n'
                f'<b>Название отряда:</b> {user.squad_name}\n',
                reply_markup=recover_request_kb(
                    scroll_callback_name='recover_user',
                    back_callback_name='admin_menu',
                    total_pages=len(to_recover),
                    page=page,
                    user_id=user.id,
                )
            )
        else:
            await call.message.edit_text(
                'На данный момент тут пусто... Попробуйте зайти позже',
                reply_markup=call.message.reply_markup,
            )


@dp.callback_query_handler(custom_cd('recover_user', keys=('user_id',)).filter(), state='*')
async def recover_request(call: types.CallbackQuery, callback_data: Dict):
    request_user_id = int(callback_data['user_id'])
    logger.debug(f'Admin {call.from_user.id} enters recover_request handler with {request_user_id=}')

    await bot.send_message(
        request_user_id,
        'Ты был восстановлен и теперь имеешь возможность снова отправить анкету',
    )
    with PostgresSession.begin() as session:
        session.query(CommonUser).filter_by(id=request_user_id).delete()

    await call.message.edit_text(
        'Пользователь был успешно восстановлен. Теперь он может отправить еще одну анкету',
        reply_markup=admin_main_menu_kb(),
    )
