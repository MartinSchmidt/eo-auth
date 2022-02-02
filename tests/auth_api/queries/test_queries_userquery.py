import pytest
from sqlalchemy import orm, exc

from auth_api.db import db
from tests.auth_api.queries.conftest import TestQueryBase

# -- Fixtures ----------------------------------------------------------------


class TestUserQueries(TestQueryBase):

    @pytest.mark.integrationtest
    def test__my_test(
        self,
        # seeded_session: db.Session,
    ):

        assert True
