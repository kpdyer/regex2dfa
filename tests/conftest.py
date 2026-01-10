"""Pytest configuration for regex2dfa tests."""

import pytest
from regex2dfa import clear_cache


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear cache before each test for isolation."""
    clear_cache()
    yield
    clear_cache()
