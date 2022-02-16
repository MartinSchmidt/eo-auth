# First party
from origin.api import TemporaryRedirect

# Local
from auth_api.controller import db_controller
from auth_api.db import db
from auth_api.state import (
    AuthState,
    redirect_to_failure,
    redirect_to_success,
)


def create_user_and_redirect(
        session: db.Session,
        state: AuthState,
) -> TemporaryRedirect:
    """
    Creates a user and an external user if they don't exist and redirects
    and redirects with success = 1

    :param session: The db session
    :param state: AuthState
    """

    if not state.terms_accepted:
        return redirect_to_failure(
            state=state,
            error_code='E4',
        )

    user = db_controller.get_or_create_user(
        session=session,
        tin=state.tin,
    )

    db_controller.attach_external_user(
        session=session,
        user=user,
        external_subject=state.external_subject,
        identity_provider=state.identity_provider,
    )

    return redirect_to_success(
        state=state,
        session=session,
        user=user,
    )
