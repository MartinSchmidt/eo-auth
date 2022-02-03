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
from auth_api.models import DbUser, DbExternalUser

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

"""
Tests to be done:
1. Test db_controller.get_token()

2. Test at token_record gets deleted

3. Test that only the correct token_record gets deleted

4. Test that signaturgruppen's api gets called with correct token_record
4.1 Test that signaturgruppen does not get called if token_record does not exists

5. Test that a new cookie is returned with correct params
- Is expired
- value is empty
- token name is correct
- path is correct

6. Test Http response body
6.1 Success=true when success
- status code is correct
6.2 Success=false when failed
- status code is correct

"""

class Testlogout(OidcCallbackEndpointsSubjectKnownBase):
    """
    Tests cases where the user is logged in and should log out
    """
    @pytest.mark.integrationtest
    def test__user_logout(
        self,
        client: FlaskClient,
        mock_session: db.Session,
        mock_get_jwk: MagicMock,
        mock_fetch_token: MagicMock,
        jwk_public: str,
        ip_token: Dict[str, Any],
        token_subject: str,
        token_idp: str,
        token_ssn: str,
        id_token_encoded: str,
        internal_subject: str,
    ) -> db.Session:

        # -- OAuth2Session object methods ------------------------------------

        mock_get_jwk.return_value = jwk_public
        mock_fetch_token.return_value = ip_token

        # -- Insert user into database ---------------------------------------


        print(id_token_encoded)
        mock_session.add(DbUser(
            subject=internal_subject,
            ssn=token_ssn,
        ))

        mock_session.add(DbExternalUser(
            subject=internal_subject,
            identity_provider=token_idp,
            external_subject=token_subject,
        ))
        """
        r = client.post(
            path=OIDC_API_LOGOUT_URL,
            json={
                'id_token': ip_token['id_token']
            }
        )
        """

        # -- Assert -----------------------------------------------------------

       # assert r.status_code == 400
