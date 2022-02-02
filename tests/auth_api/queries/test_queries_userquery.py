from uuid import uuid4
import pytest
from sqlalchemy import orm, exc

from auth_api.db import db
from auth_api.models import DbUser
from auth_api.queries import UserQuery
from tests.auth_api.queries.query_base import TestQueryBase

# -- Fixtures ----------------------------------------------------------------
user = DbUser(
    subject=str(uuid4()),
    ssn="asdasdasdasd",
)


class TestUserQueries(TestQueryBase):

    @pytest.fixture(scope='function')
    def seeded_session(self, mock_session: db.Session):
        """
        TODO
        """
        mock_session.begin()

        try:
            mock_session.add(user)
            # mock_session.add(DbTestModel(string_field='s1', integer_field=1))
            # mock_session.add(DbTestModel(string_field='s1', integer_field=2))
            # mock_session.add(DbTestModel(string_field='s2', integer_field=1))
            # mock_session.add(DbTestModel(string_field='s2', integer_field=2))

            pass
        except:  # noqa: E722
            mock_session.rollback()
        else:
            mock_session.commit()

        yield mock_session

    def test__should_register_user_login(
        self,
        seeded_session: db.Session,
    ):

        query = UserQuery(seeded_session)

        res = query.has_ssn(user.ssn).one_or_none()

        assert res is not None
        # a = 2

        # b = 3
        assert 1 == 1
