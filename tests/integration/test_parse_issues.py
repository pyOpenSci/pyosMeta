"""Test parse issues workflow"""

import pytest
from pyosmeta.models import ReviewUser


def test_parse_issue_header(process_issues, issue_list):
    """Should return a dict, should return 2 keys in the dict"""

    reviews = process_issues.parse_issues(issue_list)
    print(reviews)
    assert len(reviews.keys()) == 2
    assert list(reviews.keys())[0] == "sunpy"


@pytest.mark.parametrize(
    "file,expected",
    [
        (
            "reviews/reviewer_keyed.txt",
            [
                ReviewUser(name="", github_username="fakereviewer1"),
                ReviewUser(name="", github_username="fakereviewer2"),
            ],
        ),
        (
            "reviews/reviewer_list.txt",
            [
                ReviewUser(name="", github_username="fakereviewer1"),
                ReviewUser(name="", github_username="fakereviewer2"),
                ReviewUser(name="", github_username="fakereviewer3"),
            ],
        ),
    ],
)
def test_parse_reviewers(file, expected, process_issues, data_file):
    """Handle the multiple forms of reviewers"""
    review = data_file(file, True)
    review = process_issues.parse_issue(review)
    assert review.reviewers == expected
