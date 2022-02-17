# Standard Library
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# First party
from origin.api import (
    Cookie,
    HttpResponse,
    TemporaryRedirect,
)
from origin.auth import TOKEN_COOKIE_NAME
from origin.encrypt import aes256_decrypt
from origin.tokens import TokenEncoder
from origin.tools import url_append

# Local
from auth_api.config import (
    INTERNAL_TOKEN_SECRET,
    SSN_ENCRYPTION_KEY,
    TERMS_ACCEPT_URL,
    TERMS_URL,
    TOKEN_COOKIE_DOMAIN,
    TOKEN_COOKIE_HTTP_ONLY,
    TOKEN_COOKIE_SAMESITE,
    TOKEN_DEFAULT_SCOPES,
    TOKEN_EXPIRY_DELTA,
)
from auth_api.controller import db_controller
from auth_api.db import db
from auth_api.models import DbUser
from auth_api.user import create_user
from auth_api.state import AuthState


@dataclass
class LoginResponse:
    next_url: str
    state: AuthState


@dataclass
class NextStep:
    """
    Class used internally to return the next step before being wrapped in 
    either a TemporaryRedirect or 200 response.
    """
    next_url: str
    cookie: Optional[Cookie] = field(default=None)


state_encoder = TokenEncoder(
    schema=AuthState,
    secret=INTERNAL_TOKEN_SECRET,
)


class LoginOrchestrator:
    def __init__(
        self,
        state: AuthState,
        session: db.Session,
        user: DbUser = None
    ) -> None:
        self.state = state
        self.session = session
        self.user = user

    def redirect_next_step(
        self
    ) -> TemporaryRedirect:
        next_step = self._get_next_step()

        if next_step.cookie is not None:
            return TemporaryRedirect(
                url=next_step.next_url,
                cookies=(next_step.cookie,),
            )

        return TemporaryRedirect(
            url=next_step.next_url
        )

    def response_next_step(
        self
    ) -> HttpResponse:
        next_step = self._get_next_step()

        response = LoginResponse(
            next_url=next_step.next_url,
            state=self.state if next_step.cookie is None else None,
        )

        return HttpResponse(response)

    def _get_next_step(
        self
    ) -> NextStep:
        if self.user is not None:
            return self.return_login_success()

        if not self.state.terms_accepted:
            return NextStep(
                next_url=url_append(
                    url=self.state.fe_url,
                    path_extra='/terms',
                    query_extra={
                        'state': state_encoder.encode(self.state),
                        'terms_url': TERMS_URL,
                        'terms_accept_url': TERMS_ACCEPT_URL,
                    }
                )
            )

        self.user = create_user(
            session=self.session,
            terms_accepted=self.state.terms_accepted,
            tin=self.state.tin,
            external_subject=self.state.external_subject,
            identity_provider=self.state.identity_provider,
        )

        return self.return_login_success()

    def return_login_success(
        self
    ) -> NextStep:
        """
        After a successful action, redirect to return url with an opaque token
        and success = 1
        """
        cookie = self.log_in_user_and_create_cookie()

        # Append (or override) query parameters to the return_url provided
        # by the client, but keep all other query parameters
        actual_redirect_url = url_append(
            url=self.state.return_url,
            query_extra={'success': '1'},
        )

        return NextStep(
            next_url=actual_redirect_url,
            cookie=cookie
        )

    def log_in_user_and_create_cookie(
        self
    ) -> Cookie:
        """
        Register user login after completed registration and create 
        httponly cookie
        """
        db_controller.register_user_login(
            session=self.session,
            user=self.user,
        )

        # -- Token -----------------------------------------------------------

        issued = datetime.now(tz=timezone.utc)

        opaque_token = db_controller.create_token(
            session=self.session,
            issued=issued,
            expires=issued + TOKEN_EXPIRY_DELTA,
            subject=self.user.subject,
            scope=TOKEN_DEFAULT_SCOPES,
            id_token=aes256_decrypt(
                self.state.id_token,
                SSN_ENCRYPTION_KEY
            ),
        )

        # -- Response --------------------------------------------------------

        return Cookie(
            name=TOKEN_COOKIE_NAME,
            value=opaque_token,
            domain=TOKEN_COOKIE_DOMAIN,
            path='/',
            http_only=TOKEN_COOKIE_HTTP_ONLY,
            same_site=TOKEN_COOKIE_SAMESITE,
            secure=True,
        )
