from uuid import uuid4
from typing import Optional, List
from datetime import datetime, timezone

from energytt_platform.tokens import TokenEncoder
from energytt_platform.encrypt import aes256_encrypt
from energytt_platform.models.auth import InternalToken

from .db import db
from .queries import UserQuery, ExternalUserQuery
from .models import DbUser, DbExternalUser, DbLoginRecord, DbToken
from .config import INTERNAL_TOKEN_SECRET, SSN_ENCRYPTION_KEY


# -- Encoders & Encryption ---------------------------------------------------


internal_token_encoder = TokenEncoder(
    schema=InternalToken,
    secret=INTERNAL_TOKEN_SECRET,
)


def encrypt_ssn(ssn: str) -> str:
    """
    AES 256 encrypts social security number.

    :param ssn: Social security number
    :returns: Encrypted social security number
    """
    return aes256_encrypt(
        data=ssn,
        key=SSN_ENCRYPTION_KEY,
    )


# -- Database controller -----------------------------------------------------


class DatabaseController(object):
    """
    Controls business logic for SQL database.
    """

    def get_user_by_external_subject(
            self,
            session: db.Session,
            identity_provider: str,
            external_subject: str,
    ) -> Optional[DbUser]:
        """
        Looks up a user identified by its identity provider and the identity
        provider's subject (ID).

        :param session: Database session
        :param identity_provider: ID/name of Identity Provider
        :param external_subject: Identity Provider's subject
        :returns: User if exists, otherwise None
        """
        external_user = ExternalUserQuery(session) \
            .has_identity_provider(identity_provider) \
            .has_external_subject(external_subject) \
            .one_or_none()

        if external_user:
            return external_user.user

    def get_or_create_user(
            self,
            session: db.Session,
            ssn: str,
    ) -> DbUser:
        """
        Looks up a user by social security number.

        :param session: Database session
        :param ssn: Social security number, unencrypted
        :returns: User if exists, otherwise None
        """
        ssn_encrypted = encrypt_ssn(ssn)

        user = UserQuery(session) \
            .has_ssn(ssn_encrypted) \
            .one_or_none()

        if user is None:
            user = DbUser(
                subject=str(uuid4()),
                ssn=ssn_encrypted,
            )

            session.add(user)

        return user

    def attach_external_user(
            self,
            session: db.Session,
            user: DbUser,
            identity_provider: str,
            external_subject: str,
    ):
        """
        Creates an external user and attaches it to a user.

        :param session: Database session
        :param user: The user
        :param identity_provider: ID/name of Identity Provider
        :param external_subject: Identity Provider's subject
        """
        session.add(DbExternalUser(
            user=user,
            identity_provider=identity_provider,
            external_subject=external_subject
        ))

    def create_user(
            self,
            session: db.Session,
            ssn: str,
    ) -> DbUser:
        """
        Creates a new user.

        :param session: Database session
        :param ssn: Social security number, unencrypted
        :returns: The newly created user
        """
        ssn_encrypted = encrypt_ssn(ssn)

        user = DbUser(
            subject=str(uuid4()),
            ssn=ssn_encrypted,
        )

        session.add(user)

        return user

    def register_user_login(
            self,
            session: db.Session,
            user: DbUser,
    ):
        """
        Logs a user's login.

        TODO Add IP address?

        :param session: Database session
        :param user: The user
        """
        session.add(DbLoginRecord(
            subject=user.subject,
            created=datetime.now(tz=timezone.utc),
        ))

    def create_token(
            self,
            session: db.Session,
            issued: datetime,
            expires: datetime,
            subject: str,
            scope: List[str],
    ) -> str:
        """
        Creates an internal token with the provided scopes on behalf of
        the provided subject, and returns the opaque token.

        :param session: Database session
        :param issued: Time when token is issued
        :param expires: Time when token expires
        :param subject: The subject to create token for
        :param scope: The scopes to grant
        :returns: Opaque token
        """
        internal_token = InternalToken(
            issued=issued,
            expires=expires,
            actor=subject,
            subject=subject,
            scope=scope,
        )

        internal_token_encoded = internal_token_encoder \
            .encode(internal_token)

        opaque_token = str(uuid4())

        session.add(DbToken(
            subject=subject,
            opaque_token=opaque_token,
            internal_token=internal_token_encoded,
            issued=issued,
            expires=expires,
        ))

        return opaque_token


# -- Singletons --------------------------------------------------------------


db_controller = DatabaseController()
