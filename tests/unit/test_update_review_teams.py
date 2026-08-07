import logging
from unittest.mock import Mock

from pyosmeta.cli.update_review_teams import log_missing_user, process_user
from pyosmeta.contributors import ProcessContributors
from pyosmeta.models import ReviewUser


def test_log_missing_user_eic_logs_debug(caplog):
    """A missing `eic` is expected (older reviews predate the field), so it
    should only be logged at debug level, not warning."""
    with caplog.at_level(logging.DEBUG, logger="pyosmeta.logging"):
        log_missing_user("eic", "somepkg")

    assert any(
        record.levelno == logging.DEBUG
        and "eic" in record.message
        and "somepkg" in record.message
        for record in caplog.records
    )
    assert not any(
        record.levelno == logging.WARNING for record in caplog.records
    )


def test_log_missing_user_reviewers_fast_track_logs_debug(caplog):
    """A missing `reviewers` is expected for joss-fast-track packages, since
    they only go through editor checks."""
    with caplog.at_level(logging.DEBUG, logger="pyosmeta.logging"):
        log_missing_user("reviewers", "somepkg", is_fast_track=True)

    assert any(
        record.levelno == logging.DEBUG
        and "reviewers" in record.message
        and "somepkg" in record.message
        for record in caplog.records
    )
    assert not any(
        record.levelno == logging.WARNING for record in caplog.records
    )


def test_log_missing_user_reviewers_not_fast_track_logs_warning(caplog):
    """A missing `reviewers` on a normal (non-fast-track) package is
    unexpected and should still be logged as a warning."""
    with caplog.at_level(logging.DEBUG, logger="pyosmeta.logging"):
        log_missing_user("reviewers", "somepkg", is_fast_track=False)

    assert any(
        record.levelno == logging.WARNING
        and "reviewers" in record.message
        and "somepkg" in record.message
        for record in caplog.records
    )


def test_log_missing_user_other_roles_logs_warning(caplog):
    """A missing user for any other role (e.g. editor) is unexpected and
    should still be logged as a warning."""
    with caplog.at_level(logging.DEBUG, logger="pyosmeta.logging"):
        log_missing_user("editor", "somepkg")

    assert any(
        record.levelno == logging.WARNING
        and "editor" in record.message
        and "somepkg" in record.message
        for record in caplog.records
    )


def test_process_user_skips_when_github_user_not_found(caplog):
    """If the GitHub API can't find a user for a handle (e.g. a leftover
    placeholder or typo that slipped through parsing), `process_user` should
    log a warning and skip - not raise, and not add a broken entry to
    `contribs`."""
    processor = Mock(spec=ProcessContributors)
    # Simulates a 404 from the GitHub API: every field comes back None.
    processor.return_user_info.return_value = {
        "name": None,
        "github_username": None,
        "github_image_id": None,
    }
    user = ReviewUser(name="", github_username="ghost_user")
    contribs = {}

    with caplog.at_level(logging.WARNING, logger="pyosmeta.logging"):
        returned_user, returned_contribs = process_user(
            user, "editor", "somepkg", contribs, processor
        )

    assert returned_user is user
    assert returned_contribs == {}
    assert "ghost_user" in caplog.text
