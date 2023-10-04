from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Sequence,
    Union,
)

from rosatom_sso.database import (
    Admin,
    CommonUser,
    Statistic,
)


class UsersFileBuilder(ABC):
    @staticmethod
    @abstractmethod
    def build_xlsx(users: Sequence[Union[Admin, CommonUser]], statistics_: Sequence[Statistic]) -> str:
        ...
