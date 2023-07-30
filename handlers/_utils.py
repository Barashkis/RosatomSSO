from typing import Tuple

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType


async def file_info_from_message(message: types.Message) -> Tuple[str, str]:
    content_type = message.content_type
    if content_type == ContentType.PHOTO:
        return message.photo[-1].file_id, 'photo'
    elif content_type == ContentType.VIDEO:
        return message.video.file_id, 'video'
    else:
        return message.document.file_id, 'document'


async def update_state_data(state: FSMContext, category_key: str, **kwargs) -> None:
    await state.reset_state(with_data=False)
    async with state.proxy() as data:
        if data.get(category_key) is None:
            data[category_key] = {}
        data[category_key].update(kwargs)
