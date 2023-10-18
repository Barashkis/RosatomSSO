from aiogram.types import BotCommandScopeChat

from .config import (
    ADMIN_COMMANDS,
    COMMON_USERS_COMMANDS,
)
from .database import Admin
from .loader import PostgresSession


async def set_default_commands(dp) -> None:
    await dp.bot.set_my_commands(COMMON_USERS_COMMANDS)

    with PostgresSession.begin() as session:
        for admin in session.query(Admin).all():
            await dp.bot.set_my_commands(
                ADMIN_COMMANDS + COMMON_USERS_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin.id),
            )
