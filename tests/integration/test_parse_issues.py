"""Test parse issues workflow"""

import logging

import pytest

from pyosmeta.models import ReviewUser
from pyosmeta.models.github import Labels


def test_parse_issue_header(process_issues, issue_list):
    """Should return a dict, should return 2 keys in the dict"""

    reviews, errors = process_issues.parse_issues(issue_list)
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


def test_parse_doi_archives(process_issues, data_file):
    """
    Test handling of DOI archives in various formats.

    This is a smoke test to ensure graceful handling of these cases.
    """
    review = data_file("reviews/archives_doi.txt", True)
    review = process_issues.parse_issue(review)
    assert review.archive == "https://zenodo.org/record/8415866"
    assert review.joss == "http://joss.theoj.org/papers/10.21105/joss.01450"

    review = data_file("reviews/archives_unknown.txt", True)
    review = process_issues.parse_issue(review)
    assert review.archive is None
    assert review.joss is None

    review = data_file("reviews/archives_missing.txt", True)
    review = process_issues.parse_issue(review)
    assert review.archive is None
    assert review.joss is None

    review = data_file("reviews/archives_invalid.txt", True)

    with pytest.raises(ValueError, match="Invalid archive"):
        review = process_issues.parse_issue(review)


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
        assert review.active

    # Now add an archive label
    label_inst = Labels(
        id=1196238794,
        node_id="MDU6TGFiZWwxMTk2MjM4Nzk0",
        url="https://api.github.com/repos/pyOpenSci/software-submission/labels/archived",
        name="archived",
        description="",
        color="006B75",
        default=False,
    )
    labels = [label_inst, "another_label"]
    for issue in issue_list:
        issue.labels = labels
        review = process_issues.parse_issue(issue)
        assert not review.active

    # Handle label with missing details
    label_inst = Labels(name="test")
    labels = [label_inst, "another_label"]
    for issue in issue_list:
        issue.labels = labels
        review = process_issues.parse_issue(issue)
        assert review.labels == ["test", "another_label"]


def test_missing_community_partnerships(caplog, process_issues, data_file):
    """
    Test handling of issues with a missing "## Community Partnerships" section.

    This is a smoke test to ensure graceful handling of this case.
    """
    review = data_file("reviews/missing_community_partnerships.txt", True)
    with caplog.at_level(logging.WARNING):
        review = process_issues.parse_issue(review)
    assert "## Community Partnerships not found in the list" in caplog.text


def test_multiple_editors_and_eic(process_issues, data_file):
    """
    Test handling of issues with multiple editors and EICs.
    """
    review = data_file("reviews/multiple_editors.txt", True)
    review = process_issues.parse_issue(review)
    assert review.package_name == "fake_package"
