import pytest

from auth_api.config import (
    TOKEN_COOKIE_SAMESITE,
    TOKEN_COOKIE_HTTP_ONLY,
)


@pytest.mark.unittest
def test__token_cookie_samesite__value_omitted__should_return_default_true():
    """
    Test that omitting the 'TOKEN_COOKIE_SAMESITE' default correct.

    Should default to True.
    """
    assert TOKEN_COOKIE_SAMESITE is True


@pytest.mark.unittest
def test__token_cookie_http_only__value_omitted__should_return_default_true():
    """
    Test that omitting the 'TOKEN_COOKIE_HTTP_ONLY' default correct.

    Should default to True.
    """
    assert TOKEN_COOKIE_HTTP_ONLY is True
