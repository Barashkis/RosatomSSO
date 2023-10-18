import logging

from aiogram.types import Update

from ...loader import dp
from ._utils import errors_mapping


logger = logging.getLogger(__name__)


@dp.errors_handler()
async def catch_errors(update: Update, exception: Exception):
    content_instance = update.message or update.callback_query
    logger.debug(f'User {content_instance.from_user.id} got an exception: {exception!r}')
    if (callback := errors_mapping.get(exception.__class__)) is not None:
        await callback(content_instance)
