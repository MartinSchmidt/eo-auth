import markdown2

from dataclasses import dataclass

from origin.api import Endpoint, Context, BadRequest, TemporaryRedirect

from auth_api.db import db
from auth_api.config import TERMS_MARKDOWN_PATH
from auth_api.state import redirect_to_failure, state_encoder

from auth_api.user import create_user_and_redirect


class GetTerms(Endpoint):
    """
    An endpoint which returns the terms and conditions.
    """

    @dataclass
    class Response:
        headline: str
        terms: str
        version: str

    def handle_request(self, context: Context) -> Response:
        """
        Handle HTTP request.
        """
        with open(TERMS_MARKDOWN_PATH) as f:
            html = markdown2.markdown(f.read())

        return self.Response(
            headline='Terms and Conditions',
            terms=html,
            version='0.1',
        )


class AcceptTerms(Endpoint):
    """
    An endpoint which marks a user as having accepted terms and conditions.
    """

    @dataclass
    class Request:
        state: str
        accepted: bool
        version: str

    @db.atomic()
    def handle_request(
        self,
        request: Request,
        context: Context,
        session: db.Session,
    ) -> TemporaryRedirect:
        """
        Handle HTTP request.
        """
        # Decode state
        try:
            state = state_encoder.decode(request.state)
        except state_encoder.DecodeError:
            # TODO Handle...
            raise BadRequest()

        # TODO Verify accepted version is valid?

        state.terms_accepted = request.accepted
        state.terms_version = request.version

        if request.accepted:
            return create_user_and_redirect(
                session=session,
                state=state,
            )
        else:
            return redirect_to_failure(
                state=state,
                error_code='E4',
            )
