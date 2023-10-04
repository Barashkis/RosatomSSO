from functools import lru_cache
from typing import (
    Literal,
    Tuple,
)

from aiogram.utils.callback_data import CallbackData


__all__ = (
    'custom_cd',
)


def _perform_callback_data_keys(*args) -> Tuple[str, Literal['row'], Literal['column']]:
    return *args, 'row', 'column'  # type: ignore


@lru_cache
def custom_cd(name: str, keys: Tuple[str, ...] = tuple()) -> CallbackData:
    return CallbackData(
        name,
        *_perform_callback_data_keys(*keys)
    )
