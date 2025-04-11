"""Tests for the clean helper functions located in the utils_clean module."""

import pytest

from pyosmeta.utils_clean import (
    clean_date,
    clean_date_accepted_key,
    clean_markdown,
    clean_name,
    get_clean_user,
)


@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        # Test cases for valid dates
        ("2024-03-07T12:34:56Z", "2024-03-07"),
        ("2024-02-28T00:00:00Z", "2024-02-28"),
        # Test cases for missing dates
        (None, "missing"),
        ("missing", "missing"),
    ],
)
def test_clean_date(input_date, expected_output):
    assert clean_date(input_date) == expected_output


@pytest.mark.parametrize(
    "input_string, expected_output",
    [
        ("*Hello*", "Hello"),
        ("`Code`", "Code"),
        ("**Bold**", "Bold"),
        ("***Strong***", "Strong"),
        ("`*Code*`", "Code"),
        ("`**Code**`", "Code"),
        ("`***Code***`", "Code"),
        ("`Code***`", "Code"),
        ("***Code`", "Code"),
        ("***Code*`", "Code"),
    ],
)
def test_clean_markdown(input_string, expected_output):
    """Test that clean markdown correctly removes various markdown formatting
    elements from a text string"""
    assert clean_markdown(input_string) == expected_output


@pytest.mark.parametrize(
    "input_name, expected_output",
    [
        # Test cases for usernames with parentheses
        ("(@username)", "username"),
        ("(username)", "username"),
        # Test cases for usernames with @ symbol
        ("@username", "username"),
        # Test cases for usernames without special characters
        ("username", "username"),
    ],
)
def test_clean_name(input_name, expected_output):
    assert clean_name(input_name) == expected_output


@pytest.mark.parametrize(
    "input_dict, expected_output",
    [
        # Test case where key starts with "date_accepted"
        (
            {"date_accepted_(month-day-year)": "2024-03-07"},
            {"date_accepted": "2024-03-07"},
        ),
        (
            {"date_accepted_(month/day/year)": "2024/03/07"},
            {"date_accepted": "2024/03/07"},
        ),
        # Test where key does not start with "date_accepted"
        ({"other_key": "value"}, {"other_key": "value"}),
        (
            {"date_accepted": "2024-03-07"},
            {"date_accepted": "2024-03-07"},
        ),
    ],
)
def test_clean_date_accepted_key(input_dict, expected_output):
    assert clean_date_accepted_key(input_dict) == expected_output


@pytest.mark.parametrize(
    "input_username, expected_output",
    [
        ("githubusername", "githubusername"),
        ("githubusername name after text", "githubusername"),
        ("username (full name here)", "username"),
        ("githubusername", "githubusername"),
        ("githubusername extra text", "githubusername"),
        ("username (just the username)", "username"),
    ],
)
def test_get_clean_user(input_username, expected_output):
    assert get_clean_user(input_username) == expected_output
