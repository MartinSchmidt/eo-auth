"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest
from uuid import uuid4
from typing import Dict, Any
from unittest.mock import patch
from authlib.jose import jwt, jwk
from flask.testing import FlaskClient
from datetime import datetime, timezone, timedelta
from testcontainers.postgres import PostgresContainer

from origin.tokens import TokenEncoder
from origin.sql import SqlEngine, POSTGRES_VERSION
from origin.models.auth import InternalToken

from auth_api.app import create_app
from auth_api.endpoints import AuthState
from auth_api.config import INTERNAL_TOKEN_SECRET, TOKEN_EXPIRY_DELTA
from auth_api.db import db as _db

from .keys import PRIVATE_KEY, PUBLIC_KEY

# -- API ---------------------------------------------------------------------


@pytest.fixture(scope='function')
def client() -> FlaskClient:
    """
    Returns API test client.
    """
    return create_app().test_client


# -- OAuth2 session methods --------------------------------------------------


@pytest.fixture(scope='function')
def mock_get_jwk():
    """
    Returns a mock of OAuth2Session.get_jwk() method.
    """
    with patch('auth_api.oidc.session.get_jwk') as get_jwk:
        yield get_jwk


@pytest.fixture(scope='function')
def mock_fetch_token():
    """
    Returns a mock of OAuth2Session.fetch_token() method.
    """
    with patch('auth_api.oidc.session.fetch_token') as fetch_token:
        yield fetch_token


@pytest.fixture(scope='function')
def state_encoder() -> TokenEncoder[AuthState]:
    """
    Returns AuthState encoder with correct secret embedded.
    """
    return TokenEncoder(
        schema=AuthState,
        secret=INTERNAL_TOKEN_SECRET,
    )


@pytest.fixture(scope='function')
def internal_token_encoder() -> TokenEncoder[InternalToken]:
    """
    Returns InternalToken encoder with correct secret embedded.
    """
    return TokenEncoder(
        schema=InternalToken,
        secret=INTERNAL_TOKEN_SECRET,
    )

# -- Keys & Security ---------------------------------------------------------


@pytest.fixture(scope='function')
def jwk_public() -> str:
    """
    Mocked public key from Identity Provider.
    """
    return jwk.dumps(PUBLIC_KEY, kty='RSA')


@pytest.fixture(scope='function')
def jwk_private() -> str:
    """
    Mocked private key from Identity Provider.
    """
    return jwk.dumps(PRIVATE_KEY, kty='RSA')


# -- Tokens ------------------------------------------------------------------


@pytest.fixture(scope='function')
def token_subject() -> str:
    """
    Identity Provider's subject (used in mocked tokens).
    """
    return str(uuid4())


@pytest.fixture(scope='function')
def token_idp() -> str:
    """
    Identity Provider's name (used in mocked tokens).

    Could be, for instance, 'mitid' or 'nemid'.
    """
    return 'mitid'


@pytest.fixture(scope='function')
def token_ssn() -> str:
    """
    Identity Provider's social security number (used in mocked tokens).
    """
    return str(uuid4())


@pytest.fixture(scope='function')
def token_tin() -> str:
    """
    Identity Provider's social security number (used in mocked tokens).
    """
    return '39315041'


@pytest.fixture(scope='function')
def token_aud() -> str:
    """
    Identity Provider's aud (used in mocked tokens).
    """
    return str(uuid4())


@pytest.fixture(scope='function')
def token_transaction_id() -> str:
    """
    Identity Provider's transaction id (used in mocked tokens).
    """
    return str(uuid4())


@pytest.fixture(scope='function')
def token_issued() -> datetime:
    """
    Time of issue Identity Provider's token.
    """
    return datetime.now(tz=timezone.utc).replace(microsecond=0)


@pytest.fixture(scope='function')
def token_expires(token_issued: datetime) -> datetime:
    """
    Time of expire Identity Provider's token.
    """
    return (token_issued + TOKEN_EXPIRY_DELTA).replace(microsecond=0)


@pytest.fixture(scope='function')
def ip_token(
    id_token_encoded: str,
    userinfo_token_encoded: str,
    token_expires: datetime,
) -> Dict[str, Any]:
    """
    Mocked token from Identity Provider (unencoded).
    """
    return {
        'id_token': id_token_encoded,
        'access_token': '',
        'expires_in': 3600,
        'token_type': 'Bearer',
        'scope': 'openid mitid nemid userinfo_token',
        'userinfo_token': userinfo_token_encoded,
        'expires_at': int(token_expires.timestamp()),
    }


@pytest.fixture(scope='function')
def id_token(
        token_subject: str,
        token_idp: str,
        token_issued: datetime,
        token_expires: datetime,
        token_tin: str,
        token_aud: str,
        token_transaction_id: str,
) -> Dict[str, Any]:
    """
    Mocked ID-token from Identity Provider (unencoded).
    """
    return {
        "iss": "https://pp.netseidbroker.dk/op",
        "nbf": 1643290895,
        "iat": int(token_issued.timestamp()),
        "exp": int(token_expires.timestamp()),
        "aud": token_aud,
        "amr": [
            "nemid.otp"
        ],
        "at_hash": "MeVzZfa1Xl_eZZWPK7szfg",
        "sub": token_subject,
        "auth_time": int(token_issued.timestamp()),
        "idp": token_idp,
        "neb_sid": str(uuid4()),
        "identity_type": "professional",
        "transaction_id": token_transaction_id,
        "idp_environment": "test",
        "session_expiry": "1643305295",
        "nemid.cvr": token_tin,
        "nemid.company_name": "Energinet DataHub A/S ",
    }


@pytest.fixture(scope='function')
def id_token_encoded(
        jwk_private: str,
        id_token: Dict[str, Any],
) -> str:
    """
    Mocked ID-token from Identity Provider (encoded).
    """
    token = jwt.encode(
        header={'alg': 'RS256'},
        payload=id_token,
        key=jwk_private,
    )

    return token.decode()


@pytest.fixture(scope='function')
def userinfo_token(
        token_subject: str,
        token_idp: str,
        token_issued: datetime,
        token_expires: datetime,
        token_tin: str,
        token_aud: str,
        token_transaction_id: str,
) -> Dict[str, Any]:
    """
    Mocked userinfo-token from Identity Provider (unencoded).
    """
    return {
        "iss": "https://pp.netseidbroker.dk/op",
        "nbf": 1643290895,
        "iat": 1643290895,
        "exp": 1643291195,
        "amr": [
            "nemid.otp"
        ],
        "idp": token_idp,
        "nemid.ssn": "CVR:39315041-RID:35613330",
        "nemid.common_name": "TEST - Jakob Kristensen",
        "nemid.dn": "CN=TEST - Jakob Kristensen+SERIALNUMBER=CVR:39315041-RID:35613330,O=Energinet DataHub A/S // CVR:39315041,C=DK",  # noqa: E501
        "nemid.rid": "35613330",
        "nemid.company_name": "Energinet DataHub A/S ",
        "nemid.cvr": token_tin,
        "identity_type": "professional",
        "auth_time": int(token_issued.timestamp()),
        "sub": token_subject,
        "transaction_id": token_transaction_id,
        "aud": token_aud,
    }


@pytest.fixture(scope='function')
def userinfo_token_encoded(
        jwk_private: str,
        userinfo_token: Dict[str, Any],
) -> str:
    """
    Mocked userinfo-token from Identity Provider (encoded).
    """
    token = jwt.encode(
        header={'alg': 'RS256'},
        payload=userinfo_token,
        key=jwk_private,
    )

    return token.decode()


# # -- SQL --------------------------------------------------------------------


@pytest.fixture(scope='function')
def psql_uri():
    """
    TODO
    """
    image = f'postgres:{POSTGRES_VERSION}'

    with PostgresContainer(image) as psql:
        yield psql.get_connection_url()


@pytest.fixture(scope='function')
def db(psql_uri: str) -> SqlEngine:
    """
    TODO
    """
    with patch('auth_api.db.db.uri', new=psql_uri):
        yield _db


@pytest.fixture(scope='function')
def mock_session(db: SqlEngine) -> SqlEngine.Session:
    """
    TODO
    """
    db.apply_schema()

    with db.make_session() as session:
        yield session
