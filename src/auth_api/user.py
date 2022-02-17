# Local
from auth_api.controller import db_controller
from auth_api.db import db
from auth_api.models import DbUser
from auth_api.state import AuthState


def create_user(
        session: db.Session,
        state: AuthState
) -> DbUser:
    """
    Creates a user and an external user if they don't exist and redirects
    and redirects with success = 1

    :param session: The db session
    :param state: AuthState
    """

    if state.terms_accepted:
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

    return user
