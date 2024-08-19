"""Tests for the parse issue header workflow.
This workflow grabs the first comment from the review header and
parses out (and cleans) pyOpenSci review metadata.
"""

import pytest

from pyosmeta.parse_issues import KEYED_STRING


def test_issue_as_dict(process_issues, issue_list):
    """A method within the parse issue header that turns the
    dictionary response from github into a dict.

    Test that it captures the package name properly and the
    appropriate number of lines of information contained in the comment"""
    header, body = process_issues._split_header(issue_list[0].body)
    meta = process_issues._header_as_dict(header)
    assert meta["package_name"] == "sunpy"
    assert len(meta) == 13


@pytest.mark.parametrize(
    "text,expected",
    [
        pytest.param(
            "apple: banana", {"key": "apple", "value": "banana"}, id="base"
        ),
        pytest.param(
            "Apple :  Banana",
            {"key": "Apple", "value": "Banana"},
            id="whitespace",
        ),
        pytest.param(
            " Apple : Banana ",
            {"key": "Apple", "value": "Banana "},
            id="whitespace-leading",
        ),
        pytest.param(
            "Apple: Multiple words",
            {"key": "Apple", "value": "Multiple words"},
            id="whitespace-value",
        ),
        pytest.param(
            "Apple:banana:cherry",
            {"key": "Apple", "value": "banana:cherry"},
            id="non-greedy-key",
        ),
        pytest.param(
            "a line\nApple: banana cherry\nwatermelon",
            {"key": "Apple", "value": "banana cherry"},
            id="multiline",
        ),
        pytest.param(
            "multiword key: banana",
            {"key": "key", "value": "banana"},
            id="multiword-key",
        ),
        pytest.param(
            "multiword-key: banana",
            {"key": "multiword-key", "value": "banana"},
            id="multiword-key-hyphenated",
        ),
        pytest.param(
            "* bulleted: key",
            {"key": "bulleted", "value": "key"},
            id="bulleted-key",
        ),
    ],
)
def test_keyed_string(text, expected):
    """
    KEYED_STRING can parse a key: value pair from a string as regex results dict.

    This is super general - we want to get any key/value-ish pair whether it's right or wrong,
    we don't want to try and squeeze all normalization and cleaning into a single re, so it
    eg. doesn't strip trailing whitespace and detects mid-line keys: like that
    """
    matched = KEYED_STRING.search(text).groupdict()
    if expected:
        assert matched == expected
    else:
        assert matched is None
