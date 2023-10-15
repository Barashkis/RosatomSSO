from aiogram import (
    Bot,
    Dispatcher,
    types,
)
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from sqlalchemy.orm import sessionmaker

from .config import (
    POSTGRES_HOST,
    POSTGRES_NAME,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    REDIS_HOST,
    REDIS_PASSWORD,
    TOKEN,
)
from .database import new_engine


__all__ = (
    'bot',
    'dp',
    'postgres_engine',
    'PostgresSession',
    'storage',
)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host=REDIS_HOST, password=REDIS_PASSWORD)
dp = Dispatcher(bot, storage=storage)

postgres_engine = new_engine(
    dialect='postgresql',
    driver='psycopg2',
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    name=POSTGRES_NAME,
)
PostgresSession = sessionmaker(bind=postgres_engine)
