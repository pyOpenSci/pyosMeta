import logging

import pytest

from pyosmeta.models import ReviewModel


# We could setup some example data using fixtures and a conf.py
# Once we have a better view of the test suite.
@pytest.fixture
def review_data():
    return {
        "submitting_author": {
            "github_username": "nabobalis",
            "name": "Nabil Freij",
        },
        "all_current_maintainers": [],
        "package_name": "sunpy",
        "one-line_description_of_package": "Python for Solar Physics",
        "repository_link": "https://github.com/sunpy/sunpy",
        "version_submitted": "5.0.1",
        "eic": {"github_username": "cmarmo", "name": ""},
        "editor": {"github_username": "cmarmo", "name": ""},
        "reviewer_1": {"github_username": "Septaris", "name": ""},
        "reviewer_2": {"github_username": "nutjob4life", "name": ""},
        "archive": "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8384174.svg)](https://doi.org/10.5281/zenodo.8384174)",
        "version_accepted": "5.1.1",
        "joss_doi": "[![DOI](https://joss.theoj.org/papers/10.21105/joss.01832/status.svg)](https://joss.theoj.org/papers/10.21105/joss.01832)",
        "date_accepted": "01/18/2024",
        "categories": [
            "data-retrieval",
            "data-extraction",
            "data-processing/munging",
            "data-visualization",
        ],
    }


def test_alias_choices_validation(review_data):
    """Test that model correctly recognizes the field alias"""

    new = ReviewModel(**review_data)
    assert new.date_accepted == "2024-01-18"
    assert new.package_description == "Python for Solar Physics"
    assert new.eic.github_username == "cmarmo"


def test_is_joss_fast_track_true_when_label_present(review_data):
    """A package with the `joss-fast-track` label should be flagged as
    fast-tracked, since those only go through editor checks."""
    review_data["labels"] = ["6/pyOS-approved", "joss-fast-track"]
    new = ReviewModel(**review_data)
    assert new.is_joss_fast_track is True


def test_is_joss_fast_track_false_when_label_absent(review_data):
    """A package without the `joss-fast-track` label is a normal review."""
    review_data["labels"] = ["6/pyOS-approved"]
    new = ReviewModel(**review_data)
    assert new.is_joss_fast_track is False


@pytest.mark.parametrize(
    "maintainers",
    [
        pytest.param([], id="empty-list"),
        # `get_contributor_data` returns None when every entry was a
        # placeholder username - must not raise ValidationError.
        pytest.param(None, id="none"),
    ],
)
def test_maintainers_default_to_submitting_author(review_data, maintainers):
    """If `all_current_maintainers` is empty or None (e.g. unfilled
    template placeholders), assume the submitting author is the only
    maintainer."""
    review_data["all_current_maintainers"] = maintainers
    new = ReviewModel(**review_data)
    assert new.all_current_maintainers == [new.submitting_author]


def test_maintainers_none_logs_warning_with_package_name(review_data, caplog):
    """When maintainers come back as `None` (all placeholders), log a
    warning naming the package so it's easy to spot which review to check."""
    review_data["all_current_maintainers"] = None
    with caplog.at_level(logging.WARNING, logger="pyosmeta.logging"):
        ReviewModel(**review_data)

    assert any(
        record.levelno == logging.WARNING and "sunpy" in record.message
        for record in caplog.records
    )


def test_maintainers_not_overwritten_when_present(review_data):
    """If maintainers are already provided, don't override them with the
    submitting author."""
    review_data["all_current_maintainers"] = [
        {"github_username": "someone-else", "name": "Someone Else"}
    ]
    new = ReviewModel(**review_data)
    assert len(new.all_current_maintainers) == 1
    assert new.all_current_maintainers[0].github_username == "someone-else"
