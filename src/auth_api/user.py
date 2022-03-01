# Local
from controller import db_controller
from db import db
from models import DbUser
from state import AuthState


def create_or_get_user(
        session: db.Session,
        state: AuthState
) -> DbUser:
    """
    Create or get a user and an external user if they don't exist.

    This only happens if they have accepted terms

    :param session: The db session
    :param state: AuthState
    :return: A DbUser if a user has been created or exists, otherwise an error
    """

    if not state.terms_accepted:
        raise RuntimeError("User has not accepted terms")

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
