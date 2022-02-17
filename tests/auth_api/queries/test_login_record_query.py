import pytest

from auth_api.db import db
from auth_api.queries import LoginRecordQuery
from .query_base import TestQueryBase, USER_LOGIN_RECORD


class TestLoginRecordQuery(TestQueryBase):
    """
    Test LoginRecord queries.

    Tests cases where a subject in written into the database
    and can be returned if correct subject is called.
    """

    @pytest.mark.parametrize('user', USER_LOGIN_RECORD)
    def test__has_subject__subject_exits__return_correct_subject(
            self,
            seeded_session: db.Session,
            user,
    ):
        """
        If subject exists return correct subject.

        :param seeded_session: Mocked database session
        :param user: Current user inserted into the test
        """

        # -- Assert ----------------------------------------------------------

        assert LoginRecordQuery(seeded_session) \
            .has_subject(user['subject']) \
            .exists()

    def test__has_subject__subject_does_not_exists__return_none(
        self,
        seeded_session: db.Session,
    ):
        """
        If subject does not exists return none.

        :param seeded_session: Mocked database session
        """

        # -- Assert ----------------------------------------------------------

        assert not LoginRecordQuery(seeded_session) \
            .has_subject('INVALID_SUBJECT_LOGIN_RECORD') \
            .exists()
