"""Tests for parse helper functions located in utils_parse module."""

import pytest

from pyosmeta.utils_parse import parse_user_names


@pytest.mark.parametrize(
    "name, expected_result",
    [
        (
            "Test User (@test1user)",
            {"name": "Test User", "github_username": "test1user"},
        ),
        ("(@test2user)", {"name": "", "github_username": "test2user"}),
        (
            "Test (user) 3 (@test3user)",
            {"name": "Test user 3", "github_username": "test3user"},
        ),
        ("@test4user", {"name": "", "github_username": "test4user"}),
    ],
)
def test_parse_user_names(name, expected_result):
    assert parse_user_names(name) == expected_result
