# Standard Library
from dataclasses import dataclass, field
from typing import Optional

# First party
from origin.api import TemporaryRedirect
from origin.tools import url_append

from oidc import OIDC_ERROR_CODES


@dataclass
class AuthState:
    """
    AuthState is an intermediate token.

    AuthState is an intermediate token generated when the user requests
    an authorization URL. It encodes to a [JWT] string.
    The token is included in the authorization URL, and is returned by the
    OIDC Identity Provider when the client is redirected back.
    It provides a way to keep this service stateless.
    """

    fe_url: str
    return_url: str
    terms_accepted: Optional[bool] = field(default=False)
    terms_version: Optional[str] = field(default=None)
    id_token: Optional[str] = field(default=None)
    tin: Optional[str] = field(default=None)
    identity_provider: Optional[str] = field(default=None)
    external_subject: Optional[str] = field(default=None)


def build_failure_url(
    state: AuthState,
    error_code: str,
) -> str:
    """
    Redirecting URL.

    Builds the URL used for redirecting.
    """
    query = {
        'success': '0',
        'error_code': error_code,
        'error': OIDC_ERROR_CODES[error_code],
    }

    # Append (or override) query parameters to the return_url provided
    # by the client, but keep all other query parameters
    return url_append(
        url=state.return_url,
        query_extra=query,
    )


def redirect_to_failure(
    state: AuthState,
    error_code: str,
) -> TemporaryRedirect:
    """
    Redirect with code 307.

    Creates a 307-redirect to the return_url defined in the state with query
    parameters appended appropriately according to the error.

    :param state: State object
    :param error_code: Internal error code
    :returns: Http response
    """
    return TemporaryRedirect(
        url=build_failure_url(
            state=state,
            error_code=error_code,
        ),
    )
