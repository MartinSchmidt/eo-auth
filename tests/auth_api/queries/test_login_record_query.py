import pytest

from auth_api.db import db
from auth_api.queries import ExternalUserQuery
from .query_base import TestQueryBase, USER_EXTERNAL_LIST

class TestLoginRecordQuery(TestQueryBase):
    """
    TODO
    """
    def test__has_opaque_token__opaque_token_exits__return_correct_external_user(
            self,
    ):
        """
        TODO

        :param
        """

        # -- Act -------------------------------------------------------------

