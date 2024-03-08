"""Tests for the parse issue header workflow.
This workflow grabs the first comment from the review header and
parses out (and cleans) pyOpenSci review metadata.
"""


def test_comment_to_list(process_issues, issue_list):
    """A method within the parse issue header that turns the
    dictionary response from github into a parsable list.

    Test that it captures the package name properly and the
    appropriate number of lines of information contained in the comment"""

    pkg_name, body_data = process_issues.comment_to_list(issue_list[0])
    assert pkg_name == "sunpy"
    assert len(body_data) == 79
