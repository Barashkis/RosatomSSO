from abc import (
    ABC,
    abstractmethod,
)
from typing import Optional

from aiogram import types


class FileMessageUtils(ABC):
    @staticmethod
    @abstractmethod
    async def send(chat_id: int, caption: Optional[str], file: Optional[str]) -> None:
        ...

    @staticmethod
    @abstractmethod
    def file_id(message: types.Message) -> str:
        ...
