# Standard Library
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

# First party
from origin.encrypt import aes256_encrypt
from origin.models.auth import InternalToken
from origin.tokens import TokenEncoder

# Local
from .config import (
    INTERNAL_TOKEN_SECRET,
    SSN_ENCRYPTION_KEY,
)
from .db import db
from .models import (
    DbExternalUser,
    DbLoginRecord,
    DbToken,
    DbUser,
)
from .queries import (
    ExternalUserQuery,
    TokenQuery,
    UserQuery,
)

# -- Encoders & Encryption ---------------------------------------------------


internal_token_encoder = TokenEncoder(
    schema=InternalToken,
    secret=INTERNAL_TOKEN_SECRET,
)


def encrypt_ssn(ssn: str) -> str:
    """
    Encrypt social security number using encryption key from project config.

    :param ssn: Social security number to encrypt
    :returns: Encrypted social security number
    """
    return aes256_encrypt(
        data=ssn,
        key=SSN_ENCRYPTION_KEY,
    )


# -- Database controller -----------------------------------------------------


class DatabaseController(object):
    """Control business logic for SQL database."""

    def get_user_by_external_subject(
            self,
            session: db.Session,
            identity_provider: str,
            external_subject: str,
    ) -> Optional[DbUser]:
        """
        Look up an external subject in the database.

        :param session: Database session
        :param identity_provider: ID/name of Identity Provider
        :param external_subject: Identity Provider's subject
        :returns: if the current user exits, in the database, it will be
            returned
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
            ssn: Optional[str] = None,
            tin: Optional[str] = None,
    ) -> DbUser:
        """
        Look up a subject in the database.

        If the user does exist it returns, if not the user will be created.

        :param session: Database session
        :param ssn: Social security number, unencrypted
        :param tin: Tax Identification Number
        :returns: TODO
        """

        ssn_encrypted = encrypt_ssn(ssn) if ssn is not None else None

        query = UserQuery(session)

        if ssn is not None:
            query = query.has_ssn(ssn_encrypted)
        if tin is not None:
            query = query.has_tin(tin)

        user = query.one_or_none()

        if user is None:
            user = DbUser(
                subject=str(uuid4()),
                ssn=ssn_encrypted,
                cvr=tin,
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
        Added an external user to the database.

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
        Create a new user in the database.

        :param session: Database session
        :param ssn: Social security number, unencrypted
        :returns: TODO
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
        Log a user's login.

        :param session: Database session
        :param user: The user who logged in to the database.
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
            id_token: str,
            scope: List[str],
    ) -> str:
        """
        Create an internal token with the provided scopes.

        Create an internal token with the provided scopes on behalf of
        the provided subject, and returns the opaque token.
        The raw ID token is saved together with the token. It is used when
        logging out the user via Signaturgruppen back-channel logout via
        their API.

        :param session: Database session
        :param issued: Time when token is issued
        :param expires: Time when token expires
        :param subject: The subject to create token for
        :param id_token: ID token from Identity Provider, raw/encoded
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
            id_token=id_token,
        ))

        return opaque_token

    def get_token(
            self,
            session: db.Session,
            opaque_token: str,
            only_valid: bool = False,
    ) -> Optional[DbToken]:
        """
        Look up token by opaque token.

        :param session: Database session
        :param opaque_token: Opaque token
        :param only_valid: Set to True to only fetch token if its valid
        :returns: Token or None
        """
        query = TokenQuery(session) \
            .has_opaque_token(opaque_token)

        if only_valid:
            query = query.is_valid()

        return query.one_or_none()


# -- Singletons --------------------------------------------------------------


db_controller = DatabaseController()
