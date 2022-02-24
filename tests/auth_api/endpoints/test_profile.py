"""Tests specifically for OIDC login endpoint."""
from datetime import datetime, timezone, timedelta

import pytest
from flask.testing import FlaskClient

from origin.models.auth import InternalToken
from origin.tokens import TokenEncoder


class TestGetProfile:
    """Test of the get profile endpoint."""

    @pytest.mark.unittest
    def test__should_return_auth_url_as_json_with_correct_state(
            self,
            client: FlaskClient,
            token_encoder: TokenEncoder[InternalToken],
    ):
        """
        FIXME: Fix this test.

        This test seems to be copied and does not match up with actual title.
        """

        # -- Act -------------------------------------------------------------

        token = InternalToken(
            issued=datetime.now(tz=timezone.utc),
            expires=datetime.now(tz=timezone.utc) + timedelta(days=1),
            actor='actor',
            subject='subject',
            scope=['scope1', 'scope2'],
        )

        token_encoded = token_encoder.encode(token)

        res = client.get(
            path='/profile',
            headers={
                'Authorization': f'Bearer: {token_encoded}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200
        assert res.json == {
            'success': True,
            'profile': {
                'id': token.actor,
                'name': 'John Doe',  # TODO
                'company': 'New Company',  # TODO
                'scope': ['scope1', 'scope2'],
            }
        }
