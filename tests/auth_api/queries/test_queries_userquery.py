from uuid import uuid4
import pytest
from sqlalchemy import orm, exc

from auth_api.db import db
from auth_api.models import DbUser
from auth_api.queries import UserQuery
from tests.auth_api.queries.query_base import TestQueryBase

# -- Fixtures ----------------------------------------------------------------


USER_1 = {
    "subject": 'SUBJECT_1',
    "ssn": "SSN_1",
    "cvr": 'CVR_1'
}

USER_2 = {
    "subject": 'SUBJECT_2',
    "ssn": "SSN_2",
    "cvr": 'CVR_2'
}

USER_3 = {
    "subject": 'SUBJECT_3',
    "ssn": "SSN_3",
    "cvr": 'CVR_3'
}


USER_LIST = [
    USER_1,
    USER_2,
    USER_3,
]


class TestUserQueries(TestQueryBase):

    @pytest.fixture(scope='function')
    def seeded_session(self, mock_session: db.Session):
        """
        TODO
        """
        mock_session.begin()

        try:
            for user in USER_LIST:
                mock_session.add(DbUser(
                    subject=user['subject'],
                    ssn=user['ssn'],
                    cvr=user['cvr'],
                ))

        except:  # noqa: E722
            mock_session.rollback()
        else:
            mock_session.commit()

        yield mock_session

    @pytest.mark.parametrize('user', USER_LIST)
    def test__has_ssn__ssn_exists__return_correct_user(
        self,
        seeded_session: db.Session,
        user,
    ):

        query = UserQuery(seeded_session)

        fetched_user = query.has_ssn(user['ssn']).one_or_none()

        assert fetched_user is not None

        assert fetched_user.ssn == user['ssn']
