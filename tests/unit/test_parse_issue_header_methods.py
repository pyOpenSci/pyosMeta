import pytest

from pyosmeta.parse_issues import clean_markdown


def test_comment_to_list(process_issues, issue_list):
    """A method within the parse issue header that turns the
    dictionary response from github into a parsable list.

    Test that it captures the package name properly and the
    appropriate number of lines of information contained in the comment"""

    pkg_name, body_data = process_issues.comment_to_list(issue_list[0])
    assert pkg_name == "sunpy"
    assert len(body_data) == 79


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
