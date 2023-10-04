from functools import partial
from types import FunctionType
from typing import (
    Mapping,
    Optional,
    Type,
    Union,
)

from aiogram import types

from rosatom_sso.loader import bot

from .interfaces import FileMessageUtils


def _get_complete_send_func(func, text: Optional[str]) -> Union[partial, FunctionType]:
    if text:
        return partial(func, caption=text)

    return func


class DocumentUtils(FileMessageUtils):
    @staticmethod
    def file_id(message: types.Message) -> str:
        return message.document.file_id

    @staticmethod
    async def send(chat_id: int, caption: Optional[str], file: str) -> None:
        send_document = _get_complete_send_func(bot.send_document, caption)
        await send_document(chat_id, document=file)


class PhotoUtils(FileMessageUtils):
    @staticmethod
    def file_id(message: types.Message) -> str:
        return message.photo[-1].file_id

    @staticmethod
    async def send(caption: Optional[str], chat_id: int, file: str) -> None:
        send_photo = _get_complete_send_func(bot.send_photo, caption)
        await send_photo(chat_id, photo=file)


class VideoUtils(FileMessageUtils):
    @staticmethod
    def file_id(message: types.Message) -> str:
        return message.video.file_id

    @staticmethod
    async def send(chat_id: int, caption: Optional[str], file: str) -> None:
        send_video = _get_complete_send_func(bot.send_video, caption)
        await send_video(chat_id, video=file)


message_file_utils_dict: Mapping[str, Type[FileMessageUtils]] = {
    'document': DocumentUtils,
    'photo': PhotoUtils,
    'video': VideoUtils,
}
