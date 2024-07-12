"""Test parse issues workflow"""

import pytest
from pyosmeta.models import ReviewUser
from pyosmeta.models.github import Labels


def test_parse_issue_header(process_issues, issue_list):
    """Should return a dict, should return 2 keys in the dict"""

    reviews, errors = process_issues.parse_issues(issue_list)
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


def test_parse_bolded_keys(process_issues, data_file):
    """
    Bolding the keys in the review doesn't break the parser
    """
    review = data_file("reviews/bolded_keys.txt", True)
    review = process_issues.parse_issue(review)
    assert review.package_name == "fake_package"


def test_parse_labels(issue_list, process_issues):
    """
    `Label` models should be coerced to a string when parsing an issue
    """
    label_inst = Labels(
        id=1196238794,
        node_id="MDU6TGFiZWwxMTk2MjM4Nzk0",
        url="https://api.github.com/repos/pyOpenSci/software-submission/labels/6/pyOS-approved",
        name="6/pyOS-approved",
        description="",
        color="006B75",
        default=False,
    )
    labels = [label_inst, "another_label"]
    for issue in issue_list:
        issue.labels = labels
        review = process_issues.parse_issue(issue)
        assert review.labels == ["6/pyOS-approved", "another_label"]
