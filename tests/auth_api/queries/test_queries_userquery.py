import pytest
from sqlalchemy import orm, exc

from auth_api.db import db
from tests.auth_api.queries.conftest import TestQueryBase

# -- Fixtures ----------------------------------------------------------------


class TestUserQueries(TestQueryBase):
    """
    Tests for the queries
    Tests for the queries
    """
    @pytest.mark.integrationtest
    def test__my_test(
        self,
        seeded_session: db.Session,
    ):
        print(seeded_session)
        assert 1 == 1

