"""Tests migrations."""
import os
import pytest
import alembic.config

from auth_api.db import db as _db
from origin.sql import SqlEngine, POSTGRES_VERSION
from testcontainers.postgres import PostgresContainer
from unittest.mock import patch


# -- Fixtures ----------------------------------------------------------------

@pytest.fixture(scope='function')
def psql_uri():
    """Yield postgress uri."""

    image = f'postgres:{POSTGRES_VERSION}'

    with PostgresContainer(image) as psql:
        yield psql.get_connection_url()


@pytest.fixture(scope='function')
def db(psql_uri: str) -> SqlEngine:
    """Yield postgress engine instance."""

    with patch('auth_api.db.db.uri', new=psql_uri):
        yield _db


# -- Tests -------------------------------------------------------------------


class TestRunMigrations(object):
    """Tests relevant for migration purposes."""

    @pytest.mark.unittest
    def test__running_migrations_should_not_raise_an_error(
            self,
            db: SqlEngine
    ):
        """
        Test that migration can run successfully.

        Programmatically run the alembic script that is run in production.

        :param db: SqlEngine (required for getting a running PSQL instance)
        """

        # -- Arrange ---------------------------------------------------------

        os.chdir(os.getcwd() + '/src')
        alembic_args = [
            '--raiseerr',
            '--config=migrations/alembic.ini',
            'upgrade', 'head',
        ]

        # -- Act -------------------------------------------------------------

        alembic.config.main(argv=alembic_args)

        # -- Clean up --------------------------------------------------------

        os.chdir('..')
