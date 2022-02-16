# First party
from origin.api import Application, TokenGuard

# Local
from .config import (
    INTERNAL_TOKEN_SECRET,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_LOGIN_CALLBACK_URL,
    OIDC_SSN_VALIDATE_CALLBACK_PATH,
    OIDC_SSN_VALIDATE_CALLBACK_URL,
)
from .endpoints import (
    CreateTestToken,
    ForwardAuth,
    GetProfile,
    InspectToken,
    OpenIdLogin,
    OpenIDLoginCallback,
    OpenIdLogout,
    OpenIDSsnCallback,
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
        endpoint=OpenIDLoginCallback(url=OIDC_LOGIN_CALLBACK_URL),
    )

    # Callback, after verifying SSN
    app.add_endpoint(
        method='GET',
        path=OIDC_SSN_VALIDATE_CALLBACK_PATH,
        endpoint=OpenIDSsnCallback(url=OIDC_SSN_VALIDATE_CALLBACK_URL),
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

    return app
