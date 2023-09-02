import os

from aiogram import (
    Dispatcher,
    executor,
)

from config import temp_dir_path
from database import PostgresBase
from handlers import dp
from loader import (
    PostgresSession,
    bot,
    postgres_engine,
    storage,
)
from logger import logger
from migrations import run_migrations
from set_commands import set_default_commands


async def on_startup(dp: Dispatcher):
    import filters
    import middlewares

    if not os.path.exists(temp_dir_path):
        os.mkdir(temp_dir_path)

    PostgresBase.metadata.create_all(postgres_engine)
    run_migrations(PostgresSession, 'postgres')

    await set_default_commands(dp)

    middlewares.setup(dp)
    filters.setup(dp)

    logger.info('Bot is running')


async def on_shutdown(_):
    await bot.close()
    await storage.close()

    logger.info("Bot stopped")


def main():
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)


if __name__ == '__main__':
    main()
