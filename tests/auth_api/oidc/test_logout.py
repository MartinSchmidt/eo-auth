"""
Tests specifically for OIDC login endpoint.
"""
import pytest
from typing import Any, Dict
from datetime import datetime, timezone

from flask.testing import FlaskClient
from urllib.parse import parse_qs, urlsplit

from origin.tokens import TokenEncoder


from auth_api.db import db
from auth_api.endpoints import AuthState
from origin.auth import TOKEN_COOKIE_NAME, TOKEN_HEADER_NAME
from origin.api.testing import (
    CookieTester,
    assert_base_url,
    assert_query_parameter,
)

from auth_api.config import (
    TOKEN_COOKIE_DOMAIN,
    TOKEN_COOKIE_HTTP_ONLY,
    TOKEN_COOKIE_SAMESITE,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_SSN_VALIDATE_CALLBACK_PATH,
)
from auth_api.queries import LoginRecordQuery
from .bases import OidcCallbackEndpointsSubjectKnownBase


# -- Helpers -----------------------------------------------------------------


def assert_token(
        client: FlaskClient,
        opaque_token: str,
        expected_token: Dict[str, Any],
):
    """
    Provided an opaque token, this function translates it to an
    internal token and asserts on it's content.

    :param client:
    :param opaque_token:
    :param expected_token:
    :return:
    """
    client.set_cookie(
        server_name=TOKEN_COOKIE_DOMAIN,
        key=TOKEN_COOKIE_NAME,
        value=opaque_token,
        secure=True,
        httponly=TOKEN_COOKIE_HTTP_ONLY,
        samesite='Strict',
    )

    r_forwardauth = client.get('/token/forward-auth')

    r_inspect = client.get(
        path='/token/inspect',
        headers={TOKEN_HEADER_NAME: r_forwardauth.headers[TOKEN_HEADER_NAME]}
    )

    assert r_inspect.status_code == 200
    assert r_inspect.json == {'token': expected_token}


# -- Fixtures ----------------------------------------------------------------


@pytest.fixture(params=[
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_SSN_VALIDATE_CALLBACK_PATH,
])
def callback_endpoint_path(request) -> str:
    """
    Returns path to callback endpoint.
    """
    return request.param


# -- Tests -------------------------------------------------------------------

class TestOidcLogout(OidcCallbackEndpointsSubjectKnownBase):
    """
    todo
    """

    @pytest.mark.integrationtest
    def test__should_register_user_login(
            self,
            client: FlaskClient,
            mock_session: db.Session,
            callback_endpoint_path: str,
            internal_subject: str,
            return_url: str,
            state_encoded: str,
    ):

        # -- Act -------------------------------------------------------------

        # Login
        r1 = client.get(
            path=callback_endpoint_path,
            query_string={'state': state_encoded},
        )

        # 
        cookie_name = 'Authorization'

        cookies = CookieTester(r1.headers)

        cookie_value = cookies.get_value(TOKEN_COOKIE_NAME)

        client.set_cookie(
            server_name='domain.com',
            key=cookie_name,
            value=cookie_value
        )

        r2 = client.get(
            path='/token/forward-auth',
        )

        r3 = client.get(
            path='/logout',
            headers={
                'Authorization': r2.headers['Authorization']
            }
        )

        # -- Assert ----------------------------------------------------------


        # Check that cookie has been deleted

        # Check that oidc logout endpoint has been touched
