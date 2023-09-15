from typing import List

from sqlalchemy import (
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import (
    BigInteger,
    String,
    Text,
)


class PostgresBase(DeclarativeBase):
    pass


class Activity(PostgresBase):
    __tablename__ = 'activity'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    points: Mapped[int] = mapped_column(nullable=False)
    expires_at = mapped_column(DateTime(timezone=True), nullable=False)
    is_actual: Mapped[bool] = mapped_column(nullable=True, default=True)

    confirmations: Mapped[List['Confirmation']] = relationship(back_populates='activity')


class Admin(PostgresBase):
    __tablename__ = 'admin'

    id = mapped_column(BigInteger(), primary_key=True)


class CommonUser(PostgresBase):
    __tablename__ = 'common_user'

    id = mapped_column(BigInteger(), primary_key=True, index=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    tg_firstname: Mapped[str] = mapped_column(String(100), nullable=True)
    tg_lastname: Mapped[str] = mapped_column(String(100), nullable=True)
    wr_fullname: Mapped[str] = mapped_column(Text(), nullable=False)
    squad_name = mapped_column(Text(), nullable=False)
    points: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(250), nullable=False)
    statistic_id = mapped_column(ForeignKey('statistic.id'))

    statistic: Mapped['Statistic'] = relationship(back_populates='user')
    confirmations: Mapped[List['Confirmation']] = relationship(back_populates='user')


class Confirmation(PostgresBase):
    __tablename__ = 'confirmation'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_checked: Mapped[bool] = mapped_column(default=False, nullable=False)

    activity_id = mapped_column(ForeignKey('activity.id'))
    file_id = mapped_column(ForeignKey('file.id'))
    user_id = mapped_column(ForeignKey('common_user.id'))

    activity: Mapped['Activity'] = relationship(back_populates='confirmations')
    file: Mapped['File'] = relationship(back_populates='confirmation')
    user: Mapped['CommonUser'] = relationship(back_populates='confirmations')


class File(PostgresBase):
    __tablename__ = 'file'

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    caption: Mapped[str] = mapped_column(Text(), nullable=True)
    type: Mapped[str] = mapped_column(String(25))

    confirmation: Mapped['Confirmation'] = relationship(back_populates='file')


class Migration(PostgresBase):
    __tablename__ = '_migration'

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(default=0, nullable=False)


class Statistic(PostgresBase):
    __tablename__ = 'statistic'

    id: Mapped[int] = mapped_column(primary_key=True)
    last_activity_date = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    last_pressed_button: Mapped[str] = mapped_column(default=None, nullable=True)
    presses: Mapped[int] = mapped_column(default=0, nullable=False)

    user: Mapped['CommonUser'] = relationship(back_populates='statistic')
