from authlib.jose import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..models import OpenIDConnectToken


class SignaturgruppenToken(OpenIDConnectToken, Dict[str, Any]):
    """Token model used by the OIDC Identity Provider SignaturGruppen."""

    @classmethod
    def from_raw_token(
            cls,
            raw_token: Dict[str, Any],
            jwk: str,
    ) -> 'SignaturgruppenToken':
        """Return token from given Dict."""

        token = cls()
        token.update(raw_token)

        # Decode id_token
        token['id_token_decoded'] = \
            jwt.decode(token['id_token'], key=jwk)

        # Decode userinfo_token
        token['userinfo_token_decoded'] = \
            jwt.decode(token['userinfo_token'], key=jwk)

        return token

    @property
    def issued(self) -> datetime:
        """Time when token were issued."""

        return datetime.fromtimestamp(
            self['id_token_decoded']['iat'], tz=timezone.utc)

    @property
    def expires(self) -> datetime:
        """Time when token wil expire."""

        return datetime.fromtimestamp(
            self['id_token_decoded']['exp'], tz=timezone.utc)

    @property
    def subject(self) -> str:
        """User subject used by the Identity Provider."""

        return self['id_token_decoded']['sub']

    @property
    def provider(self) -> str:
        """TODO."""

        return self['id_token_decoded']['idp']

    @property
    def scope(self) -> List[str]:
        """Token Scope."""

        return [s for s in self['scope'].split(' ') if s.strip()]

    @property
    def id_token(self) -> str:
        """Id token used by Identity Provider."""

        return self['id_token']

    @property
    def is_private(self) -> bool:
        """TODO"""

        return self['userinfo_token_decoded']['identity_type'] == 'private'

    @property
    def is_company(self) -> bool:
        """Indicate if token belongs to a privateuser  or a company."""

        return self['userinfo_token_decoded']['identity_type'] == 'professional'  # noqa: E501

    @property
    def ssn(self) -> Optional[str]:
        """User's Social Security Number Note: Only for private users."""

        return self['userinfo_token_decoded'].get('dk.cpr')

    @property
    def tin(self) -> Optional[str]:
        """Company's Tax Identification Number(TIN)."""

        return self['userinfo_token_decoded'].get('nemid.cvr')
