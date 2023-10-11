from functools import partial

from aiogram import types
from aiogram.dispatcher import FSMContext

from ..loader import bot
from ..utils import message_file_utils_dict


async def send_message(chat_id: int, content_type: str, message: types.Message) -> None:
    if content_type == 'text':
        send_func = partial(bot.send_message, text=message.text)
    else:
        file_utils = message_file_utils_dict[content_type]
        file_id = file_utils.file_id(message)
        send_func = partial(file_utils.send, file=file_id, caption=message.caption)

    await send_func(chat_id=chat_id)


async def update_state_data(state: FSMContext, category_key: str, **kwargs) -> None:
    await state.reset_state(with_data=False)
    async with state.proxy() as data:
        if data.get(category_key) is None:
            data[category_key] = {}
        data[category_key].update(kwargs)
