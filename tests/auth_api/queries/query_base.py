"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest

from auth_api.db import db
from auth_api.models import DbUser, DbExternalUser

# -- Fixtures ----------------------------------------------------------------

USER_1 = {
    "subject": 'SUBJECT_1',
    "ssn": "SSN_1",
    "cvr": 'CVR_1'
}

USER_2 = {
    "subject": 'SUBJECT_2',
    "ssn": "SSN_2",
    "cvr": 'CVR_2'
}

USER_3 = {
    "subject": 'SUBJECT_3',
    "ssn": "SSN_3",
    "cvr": 'CVR_3'
}

USER_4 = {
    "subject": 'SUBJECT_1',
    "identity_provider": "mitid",
    "external_subject": 'SUBJECT_4'
}

USER_5 = {
    "subject": 'SUBJECT_1',
    "identity_provider": "nemid",
    "external_subject": 'SUBJECT_5'
}

USER_6 = {
    "subject": 'SUBJECT_3',
    "identity_provider": "nemid",
    "external_subject": 'SUBJECT_6'
}

USER_LIST = [
    USER_1,
    USER_2,
    USER_3,
]

USER_EXTERNAL_LIST = [
    USER_4,
    USER_5,
    USER_6,
]

class TestQueryBase:
    """
    TODO
    """

    @pytest.fixture(scope='function')
    def seeded_session(
        self,
        mock_session: db.Session,
    ) -> db.Session:
        """
        Inserts a list of mock-users and mock-external-users into the database.
        """

        # -- Insert user into database ---------------------------------------

        mock_session.begin()

        for user in USER_LIST:
            mock_session.add(DbUser(
                subject=user['subject'],
                ssn=user['ssn'],
                cvr=user['cvr'],
            ))

        for user in USER_EXTERNAL_LIST:
            mock_session.add(DbExternalUser(
                subject=user['subject'],
                identity_provider=user['identity_provider'],
                external_subject=user['external_subject'],
            ))

        mock_session.commit()

        yield mock_session


