from dataclasses import dataclass

from origin.tokens import TokenEncoder
from origin.auth import TOKEN_HEADER_NAME
from origin.models.auth import InternalToken
from origin.api import (
    Endpoint,
    Context,
    HttpResponse,
    Unauthorized,
)

from auth_api.db import db
from auth_api.queries import TokenQuery
from auth_api.config import INTERNAL_TOKEN_SECRET


class ForwardAuth(Endpoint):
    """
    ForwardAuth endpoint for Træfik.

    https://doc.traefik.io/traefik/v2.0/middlewares/forwardauth/
    """

    def handle_request(
            self,
            context: Context
    ) -> HttpResponse:
        """
        Handle HTTP request.

        :param context: Context for a single HTTP request.
        """
        if not context.opaque_token:
            raise Unauthorized()

        internal_token = self.get_internal_token(context.opaque_token)

        if internal_token is None:
            raise Unauthorized()

        return HttpResponse(
            status=200,
            headers={
                TOKEN_HEADER_NAME: f'Bearer: {internal_token}',
            },
        )

    @db.session()
    def get_internal_token(
            self,
            opaque_token: str,
            session: db.Session,
    ) -> str:
        """
        Returns the internal token if the correct opaque_token is found in
        the database.

        :param opaque_token: Primary Key Constraint
        :param session: Database session
        """
        token = TokenQuery(session) \
            .has_opaque_token(opaque_token) \
            .is_valid() \
            .one_or_none()

        if token:
            return token.internal_token


class InspectToken(Endpoint):
    """
    TODO
    """

    @dataclass
    class Response:
        token: InternalToken

    def handle_request(
            self,
            context: Context
    ) -> Response:
        """
        Handle HTTP request.

        :param context: Context for a single HTTP request.
        """
        return self.Response(
            token=context.token,
        )


class CreateTestToken(Endpoint):
    """
    Creates a new token (for testing purposes).
    """

    @dataclass
    class Request:
        token: InternalToken

    @dataclass
    class Response:
        token: str

    def handle_request(
            self,
            request: Request,
            context: Context
    ) -> Response:
        """
        Handle HTTP request.

        :param request: The internal token for the request.
        :param context: Context for a single HTTP request.
        """
        encoder = TokenEncoder(
            schema=InternalToken,
            secret=INTERNAL_TOKEN_SECRET,
        )

        return self.Response(
            token=encoder.encode(request.token),
        )
