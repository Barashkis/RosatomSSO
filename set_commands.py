from aiogram import types
from aiogram.types import BotCommandScopeChat

from database import Admin
from loader import PostgresSession


async def set_default_commands(dp):
    common_user_commands = [
        types.BotCommand('start', 'Перезапустить бота'),
        types.BotCommand('menu', 'Главное меню'),
    ]
    admin_commands = [
        types.BotCommand('admin_menu', 'Панель модератора'),
    ]

    await dp.bot.set_my_commands(common_user_commands)

    with PostgresSession.begin() as session:
        for admin in session.query(Admin).all():
            await dp.bot.set_my_commands(
                admin_commands + common_user_commands,
                scope=BotCommandScopeChat(chat_id=admin.id),
            )
