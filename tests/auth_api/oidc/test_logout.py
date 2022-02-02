"""
Tests specifically for OIDC login endpoint.
"""
from uuid import uuid4
import pytest
from typing import Any, Dict
from datetime import datetime, timedelta, timezone
import requests_mock

from flask.testing import FlaskClient
from urllib.parse import parse_qs, urlsplit

from origin.tokens import TokenEncoder
from origin.models.auth import InternalToken

from auth_api.db import db
from auth_api.endpoints import AuthState
from origin.auth import TOKEN_COOKIE_NAME, TOKEN_HEADER_NAME
from origin.api.testing import (
    CookieTester,
    assert_base_url,
    assert_query_parameter,
)

from auth_api.config import (
    OIDC_API_LOGOUT_URL,
    TOKEN_COOKIE_DOMAIN,
    TOKEN_COOKIE_HTTP_ONLY,
    TOKEN_COOKIE_SAMESITE,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_SSN_VALIDATE_CALLBACK_PATH,
)
from auth_api.models import DbToken
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
            internal_token_encoder: TokenEncoder[InternalToken],
    ):
        subject = 'subject'
        actor = 'actor'
        issued = datetime.now(tz=timezone.utc)
        expires = datetime.now(tz=timezone.utc) + timedelta(days=1)

        id_token = 'id-token'

        internal_token = InternalToken(
            issued=issued,
            expires=expires,
            actor=actor,
            subject=subject,
            scope=['scope1', 'scope2'],
        )

        internal_token_encoded = internal_token_encoder \
            .encode(internal_token)

        opaque_token = str(uuid4())

        mock_session.add(DbToken(
            subject=subject,
            opaque_token=opaque_token,
            internal_token=internal_token_encoded,
            issued=issued,
            expires=expires,
            id_token=id_token,
        ))

        mock_session.commit()

        client.set_cookie(
                server_name='domain.com',
                key=TOKEN_COOKIE_NAME,
                value=opaque_token,
            )

        with requests_mock.Mocker() as m:
            adapter = m.post(OIDC_API_LOGOUT_URL, text='', status_code=200)

            

            r = client.get(
                path='/logout',
                headers={
                    'Authorization': 'Bearer: ' + internal_token_encoded
                }
            )

            assert adapter.call_count == 1
            assert adapter.called
            assert adapter.last_request.json() == {'id_token': id_token}

        assert 1 == 1
