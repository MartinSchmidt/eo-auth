import pytest

from auth_api.db import db
from auth_api.queries import ExternalUserQuery
from .query_base import TestQueryBase, USER_EXTERNAL_LIST


class TestExternalUserQueries(TestQueryBase):
    """
    Tests cases where an external subject in written into the database
    and can be returned if correct subject is called.
    """

    @pytest.mark.parametrize('user', USER_EXTERNAL_LIST)
    def test__has_external_subject__external_subject__exists__return_correct_external_user(  # noqa: E501
            self,
            seeded_session: db.Session,
            user: dict,
    ):
        """
        Test if the current user exits in the database and returns true if
        it exists.
        :param seeded_session: Mocked database session
        :param user: Current user inserted into the test
        """

        # -- Assert ----------------------------------------------------------

        assert ExternalUserQuery(seeded_session) \
            .has_external_subject(user['external_subject']) \
            .exists()

    def test__has_external_subject__external_subject_does_not_exists__return_none(   # noqa: E501
            self,
            seeded_session: db.Session,
    ):
        """
        Test if the user exits in the database and returns false if it does
        not exist.

        :param seeded_session: Mocked database session
        """
        print()
        # -- Assert ----------------------------------------------------------

        assert not ExternalUserQuery(seeded_session) \
            .has_external_subject('invalid_external_subject') \
            .exists()

    @pytest.mark.parametrize(
        'identity_provider',
        ['midid', 'nemid', 'invalid_nemid']
    )
    def testy__has_identity_provider__identity_provider__exists__return_correct_external_user(   # noqa: E501
            self,
            seeded_session: db.Session,
            identity_provider: str,
    ):
        """
        Tests if the number of users with the given identity provider
        matches with the database
        :param seeded_session: Mocked database session
        :param identity_provider: Current identity provider inserted into
            the test
        """
        # -- Arrange ---------------------------------------------------------

        seeded_users = [
            user for user in USER_EXTERNAL_LIST
            if user['identity_provider'] == identity_provider
        ]

        # -- Act -------------------------------------------------------------

        query = ExternalUserQuery(seeded_session) \
            .has_identity_provider(identity_provider)\
            .all()

        # -- Assert ----------------------------------------------------------

        assert all(
            user.identity_provider == identity_provider
            for user in query
        )
        assert len(seeded_users) == len(query)
