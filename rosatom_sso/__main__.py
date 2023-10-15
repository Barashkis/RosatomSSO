import os

from aiogram import (
    Dispatcher,
    executor,
)

from .config import TEMP_DIR
from .handlers import dp
from .loader import (
    bot,
    storage,
)
from .logger import logger
from .set_commands import set_default_commands


async def on_startup(dp: Dispatcher):
    from . import (
        filters,
        middlewares,
    )

    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

    await set_default_commands(dp)

    middlewares.setup(dp)
    filters.setup(dp)

    logger.info('Bot is running')


async def on_shutdown(_):
    await bot.close()
    await storage.close()

    logger.info('Bot stopped')


def main():
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)


if __name__ == '__main__':
    main()
