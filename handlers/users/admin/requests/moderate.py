from typing import Dict

from aiogram import types

from config import moderation_status
from database import (
    CommonUser,
    Statistic,
)
from keyboards import (
    admin_main_menu_kb,
    common_user_main_menu_kb,
    custom_cd,
    requests_kb,
)
from loader import (
    PostgresSession,
    bot,
    dp,
)
from logger import logger


@dp.callback_query_handler(custom_cd('moderate_requests', keys=('page',)).filter(), state='*')
async def moderate_requests(call: types.CallbackQuery, callback_data: Dict):
    page = int(callback_data['page'])
    logger.debug(f'Admin {call.from_user.id} enters moderate_requests handler with {page=}')

    with PostgresSession.begin() as session:
        if to_moderate := session.query(CommonUser).filter_by(status=moderation_status).all():
            user: CommonUser = to_moderate[page - 1]
            username = '@' + user.username if user.username else 'не установлен'
            await call.message.edit_text(
                f'<b>Имя в Telegram:</b> {username}\n'
                f'<b>Фамилия и имя:</b> {user.wr_fullname}\n'
                f'<b>Название отряда:</b> {user.squad_name}\n',
                reply_markup=requests_kb(
                    scroll_callback_name='moderate_requests',
                    back_callback_name='admin_menu',
                    total_pages=len(to_moderate),
                    page=page,
                    user_id=user.id,
                )
            )
        else:
            await call.message.edit_text(
                'На данный момент тут пусто... Попробуйте зайти позже',
                reply_markup=call.message.reply_markup,
            )


@dp.callback_query_handler(custom_cd('approve_request', keys=('user_id',)).filter(), state='*')
async def approve_request(call: types.CallbackQuery, callback_data: Dict):
    request_user_id = int(callback_data['user_id'])
    logger.debug(f'Admin {call.from_user.id} enters approve_request handler with {request_user_id=}')

    await dp.current_state(user=request_user_id, chat=request_user_id).finish()
    await bot.send_message(
        request_user_id,
        'Поздравляем с присоединением к нашей программе! Расскажем о правилах:\n\n'
        '- Нажимай на кнопку "Активности", чтобы ознакомиться со списком возможных действий для получения баллов\n\n'
        '- Чтобы добавить активность к своему профилю, напиши цифру соответствующей '
        'активности в чат и прикрепи подтверждения выполнения задания\n\n'
        '- Нажав на кнопку "Мои баллы", ты узнаешь, сколько баллов ты заработал. '
        'Лучшие участники получат призы от Росатома\n\n'
        '- Кнопка "Меню" вернёт тебя в главное меню\n\n'
        'Обрати внимание, что модераторы проверяют добавленные мероприятия '
        'и имеют право не зачесть действия, которые не получат подтверждения.'
        'По всем вопросам можно написать в личные сообщения группы '
        '<a href="https://vk.com/im?sel=-25236132">"Карьера в Росатоме"</a> ВКонтакте'
    )
    await bot.send_message(
        request_user_id,
        'Это твое главное меню. Если ты потеряешь к нему доступ, воспользуйся командой /menu',
        reply_markup=common_user_main_menu_kb(),
    )
    with PostgresSession.begin() as session:
        request_user = session.get(CommonUser, request_user_id)
        request_user.status = 'Анкета одобрена'
        request_user.statistic = Statistic()

    await call.message.edit_text(
        'Заявка была успешно одобрена',
        reply_markup=admin_main_menu_kb(),
    )


@dp.callback_query_handler(custom_cd('deny_request', keys=('user_id',)).filter(), state='*')
async def deny_request(call: types.CallbackQuery, callback_data: Dict):
    request_user_id = int(callback_data['user_id'])
    logger.debug(f'Admin {call.from_user.id} enters deny_request handler with {request_user_id=}')

    await dp.current_state(user=request_user_id, chat=request_user_id).finish()
    await bot.send_message(
        request_user_id,
        'К сожалению, модераторы не нашли тебя в списке участников. '
        'Если ты уверен, что произошла ошибка, напиши нам в личные сообщения '
        '<a href="https://vk.com/im?sel=-25236132">"Карьеры в Росатоме"</a>',
    )
    with PostgresSession.begin() as session:
        session.query(CommonUser).filter_by(id=request_user_id).update({'status': 'Анкета отклонена'})

    await call.message.edit_text(
        'Заявка была успешно отклонена',
        reply_markup=admin_main_menu_kb(),
    )