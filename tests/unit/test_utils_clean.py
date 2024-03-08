"""Tests for the clean helper functions located in the utils_clean module."""

import pytest

from pyosmeta.utils_clean import clean_date, clean_markdown, clean_name


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
