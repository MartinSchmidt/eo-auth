from datetime import datetime, timedelta
from pytz import timezone

from auth_api.db import db
from auth_api.queries import TokenQuery
from .query_base import TestQueryBase


class TestTokenQueries(TestQueryBase):
    """Tests the tokens queries in the database."""

    def test__has_opaque_token__opaque_token_exits__return_correct_true(   # noqa: E501
        self,
        seeded_session: db.Session,
        opaque_token: str,
    ):
        """
        Token exists and query correct token should return True.

        :param seeded_session: Mocked database session
        :param opaque_token: Primary Key Constraint
        """

        # -- Assert ----------------------------------------------------------

        assert TokenQuery(seeded_session) \
            .has_opaque_token(opaque_token) \
            .exists()

    def test__has_opaque_token__opaque_token_does_not_exists__return_none(
        self,
        seeded_session: db.Session,
    ):
        """
        Has opaque token with invalid token should return False.

        :param seeded_session: Mocked database session
        """

        # -- Assert ----------------------------------------------------------

        assert not TokenQuery(seeded_session) \
            .has_opaque_token('INVALID_OPAQUE_TOKEN') \
            .exists()

    def test__token_is_valid__return_correct_issued_and_expires(
        self,
        seeded_session: db.Session,
        opaque_token: str,
        issued_datetime: datetime,
        expires_datetime: datetime,
    ):
        """
        If token is valid return correct token, with correct attributes.

        :param seeded_session: Mocked database session
        :param opaque_token: Primary Key Constraint
        :param issued_datetime: Indicates when a token has been issued
        :param expires_datetime: Indicates when a token will expire
        """

        # -- Act -------------------------------------------------------------

        query = TokenQuery(seeded_session) \
            .has_opaque_token(opaque_token)\
            .is_valid()\
            .one_or_none()

        # -- Assert ----------------------------------------------------------

        assert query is not None
        assert query.issued == issued_datetime
        assert query.expires == expires_datetime

    def test__token_is_valid__return_issued_and_expires_not_given_in_utc_time(
        self,
        seeded_session: db.Session,
        opaque_token: str,
    ):
        """
        A token's issued_datetime and expires_datetime should be in UTC time.

        This test if the time is given in Danish time (+1/+2) and not UTC.
        :param seeded_session: Mocked database session
        :param opaque_token: Primary Key Constraint
        """
        # -- Arrange ---------------------------------------------------------

        zone = timezone('Europe/Copenhagen')

        # -- Act -------------------------------------------------------------

        query = TokenQuery(seeded_session) \
            .has_opaque_token(opaque_token)\
            .is_valid()\
            .one_or_none()

        # -- Assert ----------------------------------------------------------

        assert query.issued != datetime.now(tz=zone)
        assert query.expires != datetime.now(tz=zone) \
               + timedelta(days=1)
