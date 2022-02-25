# First party
from origin.api import Application, TokenGuard

# Local
from .config import (
    INTERNAL_TOKEN_SECRET,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_LOGIN_CALLBACK_URL,
    TERMS_PATH,
    TERMS_ACCEPT_PATH,
)

from .endpoints import (
    # OpenID Connect:
    OpenIdLogin,
    OpenIDCallbackEndpoint,
    OpenIdLogout,
    # Profiles:
    GetProfile,
    # Tokens:
    ForwardAuth,
    InspectToken,
    CreateTestToken,
    # Terms:
    GetTerms,
    AcceptTerms,
)


def create_app() -> Application:
    """
    Create a new instance of the application.

    Create a new instance of the application and adds all the endpoints to it.

    :return: The Application instance.
    :rtype: Application
    """
    app = Application.create(
        name='Auth API',
        secret=INTERNAL_TOKEN_SECRET,
        health_check_path='/health',
    )

    # -- OpenID Connect Login ------------------------------------------------

    # Login
    app.add_endpoint(
        method='GET',
        path='/oidc/login',
        endpoint=OpenIdLogin(),
    )

    # Callback, after logging in
    app.add_endpoint(
        method='GET',
        path=OIDC_LOGIN_CALLBACK_PATH,
        endpoint=OpenIDCallbackEndpoint(url=OIDC_LOGIN_CALLBACK_URL),
    )

    # -- OpenID Connect Logout -----------------------------------------------

    app.add_endpoint(
        method='POST',
        path='/logout',
        endpoint=OpenIdLogout(),
        guards=[TokenGuard()],
    )

    # -- Profile(s) ----------------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/profile',
        endpoint=GetProfile(),
        guards=[TokenGuard()],
    )

    # -- Træfik integration --------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/token/forward-auth',
        endpoint=ForwardAuth(),
    )

    # -- Testing/misc --------------------------------------------------------

    app.add_endpoint(
        method='GET',
        path='/token/inspect',
        endpoint=InspectToken(),
    )

    app.add_endpoint(
        method='POST',
        path='/token/create-test-token',
        endpoint=CreateTestToken(),
    )

    # -- Terms ---------------------------------------------------------------

    app.add_endpoint(
        method='GET',
        path=TERMS_PATH,
        endpoint=GetTerms(),
    )

    app.add_endpoint(
        method='POST',
        path=TERMS_ACCEPT_PATH,
        endpoint=AcceptTerms(),
    )

    return app
