import pytest

from auth_api.db import db
from auth_api.queries import UserQuery
from tests.auth_api.queries.query_base import TestQueryBase, USER_LIST


class TestUserQueries(TestQueryBase):
    """
    Tests cases where a subject in written into the database
    and can be returned if correct subject is called.
    """

    @pytest.mark.parametrize('ssn', ['SSN_1', 'SSN_2', 'SSN_3'])
    def test__correct_number_of_ssns__return_correct_number_of_users(
        self,
        seeded_session: db.Session,
        ssn: str,
    ):
        """
        Test if the correct number of users, exits in the database
        and returns true if they exists.

        :param seeded_session: Mocked database session
        """

        # -- Act -------------------------------------------------------------

        seeded_users = [user for user in USER_LIST if user['ssn'] == ssn]

        print(seeded_users)
        # -- Assert ----------------------------------------------------------

        assert len(seeded_users) > 0
        assert len(seeded_users) == 1

    @pytest.mark.parametrize('user', USER_LIST)
    def test__has_ssn__ssn_exists__return_correct_user(
        self,
        seeded_session: db.Session,
        user: dict,
    ):
        """
        Test if the current user, with a given ssn, exits in the database
        and returns true if it exists.

        :param seeded_session: Mocked database session
        :param user: Current user inserted into the test
        """

        # -- Act -------------------------------------------------------------

        query = UserQuery(seeded_session) \
            .has_ssn(user['ssn']) \
            .one_or_none()

        # -- Assert ----------------------------------------------------------

        assert query is not None
        assert query.ssn == user['ssn']

    def test__has_snn__ssn_does_not_exists__return_none(
        self,
        seeded_session: db.Session,
    ):
        """
        Test if a user with an invalid ssn exits in the database and returns None if
        it does not exist.

        :param seeded_session: Mocked database session
        """
        # -- Act -------------------------------------------------------------

        query = UserQuery(seeded_session) \
            .has_ssn('invalid_ssn') \
            .one_or_none()

        # -- Assert ----------------------------------------------------------

        assert query is None

    @pytest.mark.parametrize('user',USER_LIST)
    def test__has_tin__tin_exists__return_correct_user(
        self,
        seeded_session: db.Session,
        user: dict,
    ):
        """
        Test if the current user, with a given tin, exits in the database
        and returns true if it exists.

        :param seeded_session: Mocked database session
        :param user: Current user inserted into the test
        """
        # -- Act -------------------------------------------------------------

        query = UserQuery(seeded_session) \
            .has_tin(user['cvr']) \
            .one_or_none()

        # -- Assert ----------------------------------------------------------

        assert query is not None
        assert query.cvr == user['cvr']

    def test__has_tin__tin_does_not_exists__return_none(
        self,
        seeded_session: db.Session,
    ):
        """
        Test if a user with an invalid tin exits in the database and returns None if
        it does not exist.

        :param seeded_session: Mocked database session
        """
        # -- Act -------------------------------------------------------------

        query = UserQuery(seeded_session) \
            .has_tin('invalid_tin') \
            .one_or_none()

        # -- Assert ----------------------------------------------------------

        assert query is None
