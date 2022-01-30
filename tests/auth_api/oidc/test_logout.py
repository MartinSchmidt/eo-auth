"""
Tests specifically for OIDC login endpoint.
"""
import pytest
from typing import Any, Dict
from datetime import datetime, timezone

from unittest.mock import MagicMock
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

from auth_api.config import OIDC_API_LOGOUT_URL

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
from ..conftest import mock_get_jwk, mock_fetch_token, jwk_public, ip_token


class Testlogout:
    """
    Tests cases where the user accepts the terms and conditions
    """

    @pytest.mark.integrationtest
    def test__user_logout(
        self,
        client: FlaskClient,
        mock_session: db.Session,
        mock_get_jwk: MagicMock,
        mock_fetch_token: MagicMock,
        state_encoder: TokenEncoder[AuthState],
        jwk_public: str,
        ip_token: Dict[str, Any],
        token_issued: datetime,
        token_expires: datetime,
        userinfo_token: str,
    ):
        # -- Arrange ----------------------------------------------------------


        state = AuthState(
            fe_url='http://foobar.com',
            return_url='http://redirect-here.com/foobar',
        )

        state_encoded = state_encoder.encode(state)
        mock_get_jwk.return_value = jwk_public
        mock_fetch_token.return_value = ip_token

        print(userinfo_token)
        # -- Act --------------------------------------------------------------

        r = client.post(
            path=OIDC_API_LOGOUT_URL,
            json={
                'id_token': ip_token['id_token']
            }
        )


        # -- Assert -----------------------------------------------------------

        assert r.status_code == 400
