from aiogram import Dispatcher

from .activity import TrackUserActivityMiddleware


__all__ = (
    'setup',
)


def setup(dp: Dispatcher) -> None:
    dp.middleware.setup(TrackUserActivityMiddleware())
