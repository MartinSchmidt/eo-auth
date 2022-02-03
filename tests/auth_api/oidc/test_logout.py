"""
Tests specifically for OIDC logout endpoint.
"""
from uuid import uuid4
import pytest
from typing import Any, Dict
from datetime import datetime, timedelta, timezone
import requests_mock

from flask.testing import FlaskClient

from origin.tokens import TokenEncoder
from origin.models.auth import InternalToken

from auth_api.db import db
from origin.auth import TOKEN_COOKIE_NAME, TOKEN_HEADER_NAME

from origin.api.testing import CookieTester


from auth_api.config import (
    OIDC_API_LOGOUT_URL,
    TOKEN_COOKIE_DOMAIN,
    TOKEN_COOKIE_HTTP_ONLY,
    TOKEN_COOKIE_SAMESITE,
)
from auth_api.models import DbToken


# -- Fixtures ----------------------------------------------------------------
@pytest.fixture(scope='function')
def id_token() -> str:
    """
    Returns the a dummy idtoken used for the OpenID Connect identity provider.
    """
    return 'id-token'


@pytest.fixture(scope='function')
def subject() -> str:
    """
    Returns the subject.
    """
    return 'subject'


@pytest.fixture(scope='function')
def actor() -> str:
    """
    Returns an actor name.
    """
    return 'actor'


@pytest.fixture(scope='function')
def opaque_token() -> str:
    """
    Returns a opaque token, which are the token
    that are actual visible to the frontend.
    """
    return str(uuid4())


@pytest.fixture(scope='function')
def issued_datetime() -> datetime:
    """
    A datetime that indicates when an token has been issued
    """
    return datetime.now(tz=timezone.utc)


@pytest.fixture(scope='function')
def expires_datetime() -> datetime:
    """
    A datetime that indicates when an token will expire
    """
    return datetime.now(tz=timezone.utc) + timedelta(days=1)


@pytest.fixture(scope='function')
def internal_token(
    subject: str,
    expires_datetime: datetime,
    issued_datetime: datetime,
    actor: str,
) -> InternalToken:
    """
    Returns the internal token used within the system itself.
    """
    return InternalToken(
        issued=issued_datetime,
        expires=expires_datetime,
        actor=actor,
        subject=subject,
        scope=['scope1', 'scope2'],
    )


@pytest.fixture(scope='function')
def internal_token_encoded(
    internal_token: InternalToken,
    internal_token_encoder: TokenEncoder[InternalToken],
) -> str:
    """
    Returns the internal token in encoded string format. 
    """
    return internal_token_encoder \
        .encode(internal_token)


@pytest.fixture(scope='function')
def seeded_session(
        mock_session: db.Session,
        internal_token_encoded: InternalToken,
        id_token: str,
        subject: str,
        expires_datetime: datetime,
        issued_datetime: datetime,
        opaque_token: str,
) -> db.Session:
    """
    Seeds the database with a token, which make it seem like a user has been logged in.
    """

    mock_session.add(DbToken(
        subject=subject,
        opaque_token=opaque_token,
        internal_token=internal_token_encoded,
        issued=issued_datetime,
        expires=expires_datetime,
        id_token=id_token,
    ))

    mock_session.commit()


@pytest.fixture(scope='function')
def request_mocker() -> requests_mock:
    """
    A request mock which can be used to mock requests responses made to eg. OpenID Connect api endpoints.
    """

    with requests_mock.Mocker() as m:
        yield m

# -- Tests -------------------------------------------------------------------


class TestOidcLogout:
    """
    Tests the ODIC Logout implementation.
    """

    @pytest.mark.integrationtest
    def test__logout__calling_oidc_logout_endpoint_with_correct_correct_body(
            self,
            client: FlaskClient,
            seeded_session: db.Session,
            request_mocker: requests_mock,
            internal_token_encoded: str,
            opaque_token: str,
            id_token: str,
    ):
        """When logging out, this is tests that the HTTP request payload
        sent to the OIDC logout endpoint, is actually correct.

        Args:
            client (FlaskClient): API client
            seeded_session (db.Session): Seeded database session
            request_mocker (requests_mock): Used for mocking OIDC logout response
            internal_token_encoded (str): Encoded external token saved in database
            opaque_token (str): Token used in the frontend
            id_token (str): Token used by the OIDC identity provider
        """

        # -- Arrange ---------------------------------------------------------

        # Create a cookie required for authentication
        client.set_cookie(
            server_name='domain.com',
            key=TOKEN_COOKIE_NAME,
            value=opaque_token,
        )

        # Alter the the OIDC api logout response
        # to give back a logout success response.
        adapter = request_mocker.post(
            OIDC_API_LOGOUT_URL,
            text='',
            status_code=200
        )

        # -- Act -------------------------------------------------------------

        client.post(
            path='/logout',
            headers={
                'Authorization': 'Bearer: ' + internal_token_encoded
            }
        )

        # -- Assert ----------------------------------------------------------

        assert adapter.call_count == 1

        # Make sure that the request payload
        # sent to the OIDC logout url is correct
        assert adapter.last_request.json() == {'id_token': id_token}

    def test__logout_success__returned_cookie_is_expired(
            self,
            client: FlaskClient,
            seeded_session: db.Session,
            request_mocker: requests_mock,
            internal_token_encoded: str,
            opaque_token: str,
            id_token: str,
    ):
        """When logging out, this is tests that the new returned cookie
        has expired.

        Args:
            client (FlaskClient): API client
            seeded_session (db.Session): Seeded database session
            request_mocker (requests_mock): Used for mocking OIDC logout response
            internal_token_encoded (str): Encoded external token saved in database
            opaque_token (str): Token used in the frontend
            id_token (str): Token used by the OIDC identity provider
        """

        # -- Arrange ---------------------------------------------------------

        # Create a cookie required for authentication
        client.set_cookie(
            server_name='domain.com',
            key=TOKEN_COOKIE_NAME,
            value=opaque_token,
        )

        # Alter the the OIDC api logout response
        # to give back a logout success response.
        request_mocker.post(
            OIDC_API_LOGOUT_URL,
            text='',
            status_code=200
        )

        # -- Act -------------------------------------------------------------

        response = client.post(
            path='/logout',
            headers={
                'Authorization': 'Bearer: ' + internal_token_encoded
            }
        )

        # -- Assert ----------------------------------------------------------

        cookies = CookieTester(response.headers) \
            .assert_has_cookies(TOKEN_COOKIE_NAME)

        # Get auth cookie
        auth_cookie = cookies.cookies[TOKEN_COOKIE_NAME]

        assert auth_cookie.value == ''
        assert auth_cookie['path'] == '/'
        assert auth_cookie['domain'] == TOKEN_COOKIE_DOMAIN
        assert auth_cookie['httponly'] == TOKEN_COOKIE_HTTP_ONLY
        assert auth_cookie['samesite'] == 'Strict'
        assert auth_cookie['secure'] is True

        # Get time when cookie expires
        expires_datatime = datetime.strptime(
            auth_cookie['expires'],
            "%a, %d %b %Y %H:%M:%S GMT",
        )

        assert expires_datatime < datetime.now()
