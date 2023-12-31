import asyncio
import logging
import os
from concurrent.futures import ProcessPoolExecutor

from aiogram import types
from sqlalchemy import text

from ......config import (
    MODERATION_STATUS,
    REQUEST_DENIED_STATUS,
)
from ......database import CommonUser
from ......keyboards import custom_cd
from ......loader import (
    PostgresSession,
    dp,
)
from .._utils import CommonUsersFileBuilder


logger = logging.getLogger(__name__)


@dp.callback_query_handler(custom_cd('inspect_common_users_csv_file').filter(), state='*')
async def inspect_common_users_by_csv_file(call: types.CallbackQuery):
    logger.debug(f'Admin {call.from_user.id} enters inspect_common_users_by_csv_file handler')
    with PostgresSession.begin() as session:
        session.execute(text('SET timezone = \'Europe/Moscow\';'))
        if to_inspect := session.query(CommonUser).order_by(CommonUser.created_at.desc()).filter(
                CommonUser.status != REQUEST_DENIED_STATUS,
                CommonUser.status != MODERATION_STATUS,
        ).all():
            statistics_ = [user.statistic for user in to_inspect]

            loop = asyncio.get_running_loop()
            with ProcessPoolExecutor() as pool:
                fp = await loop.run_in_executor(pool, CommonUsersFileBuilder.build_xlsx, to_inspect, statistics_)

            await call.answer()
            with open(fp, 'rb') as file:
                await call.message.answer_document(document=file)
            os.remove(fp)
        else:
            await call.message.edit_text(
                'На данный момент тут пусто... Попробуйте зайти позже',
                reply_markup=call.message.reply_markup,
            )
