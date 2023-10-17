import logging
import os
from glob import glob
from pathlib import Path
from textwrap import dedent

from sqlalchemy import (
    TextClause,
    text,
)
from sqlalchemy.orm import sessionmaker


__all__ = (
    'migrate_postgres',
)

from rosatom_sso.database import Migration


logger = logging.getLogger('rosatom_sso.migrations')

migrations_dir = 'versions'


class MigrationError(Exception):
    pass


def _read_migration(filepath: Path) -> TextClause:
    statements = []
    with open(filepath, encoding='utf-8') as file:
        for line in file.readlines():
            statements.append(line)

    return text('\n'.join(statements))


def migrate_postgres(s: sessionmaker, db_folder: str) -> None:
    with s.begin() as session:
        session.execute(
            text(
                dedent(
                    '''
                    CREATE TABLE IF NOT EXISTS _migration (
                        id SERIAL,
                        version INTEGER DEFAULT 0
                    );
                    '''
                )
            )
        )
        migration_record = session.query(Migration).first()
        if migration_record is None:
            session.add(Migration())
            migration_record = session.query(Migration).first()
        current_version = migration_record.version

        workdir = str(Path('migrations', db_folder))
        unused_migrations = []
        for migration in glob(str(Path(workdir, migrations_dir, f'{"[0-9]" * 3}.sql'))):
            if os.path.isfile(migration):
                if (version := int(Path(migration).stem)) > current_version:
                    unused_migrations.append(version)

        if unused_migrations:
            unused_migrations.sort()
            expected_migrations = [i for i in range(current_version + 1, unused_migrations[-1] + 1)]
            if len(expected_migrations) != len(unused_migrations):
                raise MigrationError(
                    'Found missing migration versions: '
                    f'{", ".join(sorted(map(str, set(expected_migrations) - set(unused_migrations))))}.'
                )

            for version in unused_migrations:
                filepath = Path(workdir, migrations_dir, f'{str(version).rjust(3, "0")}.sql')
                session.execute(_read_migration(filepath))

                logger.info(f'Execute migration {filepath}')
                migration_record.version += 1
        logger.info('All migrations are active')
