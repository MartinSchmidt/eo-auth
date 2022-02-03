import pytest

from auth_api.db import db
from auth_api.queries import ExternalUserQuery
from .query_base import TestQueryBase, USER_EXTERNAL_LIST


class TestTokenQueries(TestQueryBase):
    """
    TODO
    """
