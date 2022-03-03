# First party
from origin.api import TokenGuard
from fastapi import FastAPI, Request

# Local
from config import (
    INTERNAL_TOKEN_SECRET,
    OIDC_LOGIN_CALLBACK_PATH,
    OIDC_LOGIN_CALLBACK_URL,
    INVALIDATE_PENDING_LOGIN_PATH,
)

from endpoints import (
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
async def logout(request: Request):
    TokenGuard().validate(request.client.host)
    return OpenIdLogout()

# -- Profile(s) ----------------------------------------------------------


@app.get("/profile")
async def profile(request: Request):
    TokenGuard().validate(request.client.host)
    return GetProfile()

# -- Træfik integration --------------------------------------------------


@app.get("/token/forward-auth")
async def foward_auth():
    return ForwardAuth()

# -- Testing/misc --------------------------------------------------------


@app.get("/token/inspect")
async def token_inspect():
    return InspectToken()


@app.post("token/create-test-token")
async def create_test_token():
    return CreateTestToken()

# -- Terms ---------------------------------------------------------------


@app.get("/terms")
async def terms():
    return GetTerms()


@app.post("/terms/accept")
async def terms_accept():
    return AcceptTerms()
