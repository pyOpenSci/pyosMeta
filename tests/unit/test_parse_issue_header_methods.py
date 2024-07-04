"""Tests for the parse issue header workflow.
This workflow grabs the first comment from the review header and
parses out (and cleans) pyOpenSci review metadata.
"""


def test_issue_as_dict(process_issues, issue_list):
    """A method within the parse issue header that turns the
    dictionary response from github into a dict.

    Test that it captures the package name properly and the
    appropriate number of lines of information contained in the comment"""
    header, body = process_issues._split_header(issue_list[0].body)
    meta = process_issues._header_as_dict(header)
    assert meta["package_name"] == "sunpy"
    assert len(meta) == 13
