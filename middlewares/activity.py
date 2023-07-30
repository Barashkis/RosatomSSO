from typing import Dict

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from sqlalchemy import func

from database import CommonUser
from loader import PostgresSession


class TrackUserActivityMiddleware(BaseMiddleware):
    async def on_process_callback_query(self, call: types.CallbackQuery, data: Dict) -> None:
        try:
            callback_data = data['callback_data']
            row, column = int(callback_data['row']), int(callback_data['column'])
        except KeyError:
            callback_data = call.data.split(':')
            row, column = int(callback_data[-2]), int(callback_data[-1])

        with PostgresSession.begin() as session:
            if user := session.query(CommonUser).get(call.from_user.id):
                if user_stat := user.statistic:
                    user_stat.presses += 1
                    user_stat.last_pressed_button = (
                        call.message.reply_markup.inline_keyboard[row][column].text
                    )

    async def on_process_message(self, message: types.Message, _) -> None:
        with PostgresSession.begin() as session:
            if user := session.query(CommonUser).get(message.from_user.id):
                if user_stat := user.statistic:
                    user_stat.last_activity_date = func.now()
