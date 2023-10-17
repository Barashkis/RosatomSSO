from rosatom_sso.loader import PostgresSession
from rosatom_sso.logger import setup_logger

from .postgres import migrate_postgres


def run_migrations():
    setup_logger()

    migrate_postgres(PostgresSession, 'postgres')


if __name__ == '__main__':
    run_migrations()
