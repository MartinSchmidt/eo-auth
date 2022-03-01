# First party
import secrets
from origin.api import Application, TokenGuard
from fastapi import FastAPI

# Local
from .config import (
    INTERNAL_TOKEN_SECRET,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_LOGIN_CALLBACK_URL,
    INVALIDATE_PENDING_LOGIN_PATH,
)

from .endpoints import (
    # OpenID Connect:
    OpenIdLogin,
    OpenIDCallbackEndpoint,
    OpenIdInvalidateLogin,
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


def create_app() -> FastAPI:
    """
    Create a new instance of the application and adds all the endpoints to it.

    :return: The Application instance.
    :rtype: Application
    """

    app = FastAPI(
        title="Auth API",
        secret=INTERNAL_TOKEN_SECRET,
    )

    # Health check
    @app.get("/health")
    async def health_check():
        return {"message": "I'm alive"}

    # -- OpenID Connect ------------------------------------------------------

    # Login
    @app.get("/oidc/login")
    async def login():
        return OpenIdLogin()

    # Callback, after logging in
    @app.get(OIDC_LOGIN_CALLBACK_PATH)
    async def callback():
        return OpenIDCallbackEndpoint(url=OIDC_LOGIN_CALLBACK_URL)

    # Invalidate login
    @app.post(INVALIDATE_PENDING_LOGIN_PATH)
    async def invalidate_login():
        return OpenIdInvalidateLogin()

    # Logout
    @app.post("/logout")
    async def logout():
        TokenGuard()
        return OpenIdLogout()

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
        path='/terms',
        endpoint=GetTerms(),
    )

    app.add_endpoint(
        method='POST',
        path='/terms/accept',
        endpoint=AcceptTerms(),
    )

    return app
