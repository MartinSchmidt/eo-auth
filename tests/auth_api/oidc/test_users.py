# Standard Library
from typing import Any, Dict
from unittest.mock import MagicMock
from uuid import uuid4

# Third party
import pytest

# Local
from auth_api.db import db
from auth_api.endpoints import AuthState
from auth_api.models import DbExternalUser, DbUser
from auth_api.queries import UserQuery
from auth_api.user import create_user

# -- Tests --------------------------------------------------------------------

class TestCreateUser:

    # -- Fixtures -------------------------------------------------------------
    """
    Tests cases when a new user is created
    """
    @pytest.fixture(scope='function')
    def internal_subject(self) -> str:
        """
        Our internal subject
        """
        return str(uuid4())

    @pytest.fixture(scope='function')
    def return_url(self) -> str:
        """
        Client's return_url
        """
        return 'https://redirect-here.com/foobar?foo=bar'

    @pytest.fixture(scope='function')
    def fe_url(self) -> str:
        """
        Client's fe_url
        """
        return 'https://foobar.com/'

    @pytest.fixture(scope='function')
    def seeded_session(
            self,
            mock_session: db.Session,
            mock_get_jwk: MagicMock,
            mock_fetch_token: MagicMock,
            jwk_public: str,
            ip_token: Dict[str, Any],
            token_subject: str,
            token_idp: str,
            token_tin: str,
            internal_subject: str,
    ) -> db.Session:
        """
        Inserts a mock-user into the database.
        """

        # -- OAuth2Session object methods ------------------------------------

        mock_get_jwk.return_value = jwk_public
        mock_fetch_token.return_value = ip_token

        # -- Insert user into database ---------------------------------------

        mock_session.begin()

        mock_session.add(DbUser(
            subject=internal_subject,
            cvr=token_tin,
        ))

        mock_session.add(DbExternalUser(
            subject=internal_subject,
            identity_provider=token_idp,
            external_subject=token_subject,
        ))

        mock_session.commit()

        return mock_session

    def test__create_user__if_user_does_not_exist__it_should_insert_a_user(
        self,
        mock_session: db.Session,
        token_tin: str,
        token_idp: str,
        token_subject: str,
        id_token_encrypted: str,
    ):
        # -- Arrange ----------------------------------------------------------

        state = AuthState(
            fe_url='https://foobar.com',
            return_url='https://redirect-here.com/foobar',
            tin=token_tin,
            id_token=id_token_encrypted,
            terms_accepted=True,
            terms_version='0.1',
            identity_provider=token_idp,
            external_subject=token_subject,
        )

        # -- Act --------------------------------------------------------------

        create_user(
            session=mock_session,
            terms_accepted=state.terms_accepted,
            tin=state.tin,
            external_subject=state.external_subject,
            identity_provider=state.identity_provider,
        )

        # -- Assert -----------------------------------------------------------

        assert UserQuery(mock_session) \
            .has_tin(token_tin) \
            .count() == 1

    @pytest.mark.integrationtest
    def test__create_user__when_a_user_with_same_tin_already_exists__it_should_not_insert_a_user(  # noqa: E501
        self,
        seeded_session: db.Session,
        token_tin: str,
        token_idp: str,
        token_subject: str,
        id_token_encrypted: str,
    ):
        # Attempts to add a user with the same tin as an existing user
        # It should not add another user
        
        # -- Arrange ----------------------------------------------------------

        state = AuthState(
            fe_url='https://foobar.com',
            return_url='https://redirect-here.com/foobar',
            tin=token_tin,
            id_token=id_token_encrypted,
            terms_accepted=True,
            terms_version='0.1',
            identity_provider=token_idp,
            external_subject=token_subject,
        )

        # -- Act --------------------------------------------------------------

        create_user(
            session=seeded_session,
            terms_accepted=state.terms_accepted,
            tin=state.tin,
            external_subject=state.external_subject,
            identity_provider=state.identity_provider,
        )

        # -- Assert -----------------------------------------------------------

        assert UserQuery(seeded_session) \
            .has_tin(token_tin) \
            .count() == 1

    @pytest.mark.integrationtest
    def test__create_user__when_terms_have_not_been_accepted__it_should_not_insert_a_user(  # noqa: E501
        self,
        mock_session: db.Session,
        token_tin: str,
        token_idp: str,
        token_subject: str,
        id_token_encrypted: str,
    ):
        """
        When terms have not been accepted, we cannot create a user 
        This checks if a user is created when terms have been declined
        """
        # -- Arrange ----------------------------------------------------------

        state = AuthState(
            fe_url='https://foobar.com',
            return_url='https://redirect-here.com/foobar',
            tin=token_tin,
            id_token=id_token_encrypted,
            terms_accepted=False,
            terms_version='0.1',
            identity_provider=token_idp,
            external_subject=token_subject,
        )

        # -- Act --------------------------------------------------------------

        create_user(
            session=mock_session,
            terms_accepted=state.terms_accepted,
            tin=state.tin,
            external_subject=state.external_subject,
            identity_provider=state.identity_provider,
        )

        # -- Assert -----------------------------------------------------------

        assert UserQuery(mock_session) \
            .has_tin(token_tin) \
            .count() == 0
