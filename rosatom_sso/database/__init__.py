from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)

from .postgres import (
    Activity,
    Admin,
    CommonUser,
    Confirmation,
    File,
    Migration,
    PostgresBase,
    Statistic,
)


__all__ = (
    'Activity',
    'Admin',
    'CommonUser',
    'Confirmation',
    'File',
    'Migration',
    'PostgresBase',
    'Statistic',
    'new_engine',
)


def new_engine(dialect, driver, user, password, host, name) -> Engine:
    url_object = URL.create(
        f'{dialect}+{driver}',
        username=user,
        password=password,
        host=host,
        database=name,
    )
    return create_engine(url_object)
