import pytest

from pyosmeta.cli.process_reviews import update_gh_meta
from pyosmeta.github_api import GitHubAPI, GitHubAPIError
from pyosmeta.models import ReviewModel
from pyosmeta.models.base import GhMeta


@pytest.fixture
def review():
    return ReviewModel(
        package_name="sunpy",
        repository_link="https://github.com/sunpy/sunpy",
    )


@pytest.fixture
def endpoints():
    return {"sunpy": {"owner": "sunpy", "repo_name": "sunpy"}}


@pytest.fixture
def new_meta():
    """A freshly fetched gh_meta dict, as returned by get_repo_meta_github."""
    return {
        "name": "sunpy",
        "description": "Python for Solar Physics",
        "created_at": "2013-01-01",
        "stargazers_count": 999,
        "watchers_count": 10,
        "open_issues_count": 5,
        "forks_count": 100,
        "documentation": "https://sunpy.org",
        "contrib_count": 200,
        "last_commit": "2026-01-01",
    }


@pytest.fixture
def old_meta():
    """Previously saved metrics, as loaded from the live packages.yml."""
    return GhMeta(
        name="sunpy",
        description="Python for Solar Physics",
        created_at="2013-01-01",
        stargazers_count=500,
        watchers_count=8,
        open_issues_count=3,
        forks_count=90,
        documentation="https://sunpy.org",
        contrib_count=150,
        last_commit="2025-01-01",
    )


class TestGetMetrics:
    """Fetch-only behavior: get_metrics does not gap-fill from existing data."""

    def test_uses_fresh_data_when_fetch_succeeds(
        self, mocker, review, endpoints, new_meta
    ):
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api, "get_repo_meta_github", return_value=new_meta
        )

        reviews = github_api.get_metrics(endpoints, {"sunpy": review})

        assert reviews["sunpy"].gh_meta.stargazers_count == 999

    def test_leaves_none_when_fetch_fails(self, mocker, review, endpoints):
        """Failed fetch leaves gh_meta empty; gap-fill is update_gh_meta's job."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api, "get_repo_meta_github", return_value=None
        )

        reviews = github_api.get_metrics(endpoints, {"sunpy": review})

        assert reviews["sunpy"].gh_meta is None

    def test_unexpected_exception_leaves_none(self, mocker, review, endpoints):
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api,
            "get_repo_meta_github",
            side_effect=RuntimeError("boom"),
        )

        reviews = github_api.get_metrics(endpoints, {"sunpy": review})

        assert reviews["sunpy"].gh_meta is None

    def test_fatal_error_leaves_none_for_current_package(
        self, mocker, review, endpoints
    ):
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api,
            "get_repo_meta_github",
            side_effect=GitHubAPIError("401 Unauthorized"),
        )

        reviews = github_api.get_metrics(endpoints, {"sunpy": review})

        assert reviews["sunpy"].gh_meta is None

    def test_fatal_error_stops_remaining_packages_from_being_fetched(
        self, mocker
    ):
        endpoints = {
            "sunpy": {"owner": "sunpy", "repo_name": "sunpy"},
            "other-pkg": {"owner": "other", "repo_name": "other-pkg"},
        }
        reviews_input = {
            "sunpy": ReviewModel(
                package_name="sunpy",
                repository_link="https://github.com/sunpy/sunpy",
            ),
            "other-pkg": ReviewModel(
                package_name="other-pkg",
                repository_link="https://github.com/other/other-pkg",
            ),
        }
        github_api = GitHubAPI()
        mock_fetch = mocker.patch.object(
            github_api,
            "get_repo_meta_github",
            side_effect=GitHubAPIError("403 rate limit exhausted"),
        )

        reviews = github_api.get_metrics(endpoints, reviews_input)

        mock_fetch.assert_called_once()
        assert reviews["sunpy"].gh_meta is None
        assert reviews["other-pkg"].gh_meta is None

    def test_skips_non_github_hosts(self, mocker):
        review = ReviewModel(
            package_name="example",
            repository_link="https://gitlab.com/example/example",
        )
        github_api = GitHubAPI()
        mock_fetch = mocker.patch.object(github_api, "get_repo_meta_github")

        reviews = github_api.get_metrics(
            {"example": {"owner": "example", "repo_name": "example"}},
            {"example": review},
        )

        mock_fetch.assert_not_called()
        assert reviews["example"].gh_meta is None


class TestUpdateGhMeta:
    """Gap-fill from previously published packages.yml after a fetch."""

    def test_prefers_fresh_data(self, review, new_meta, old_meta):
        review.gh_meta = GhMeta(**new_meta)

        reviews = update_gh_meta({"sunpy": old_meta}, {"sunpy": review})

        assert reviews["sunpy"].gh_meta.stargazers_count == 999

    def test_fills_from_existing_when_fetch_left_none(self, review, old_meta):
        assert review.gh_meta is None

        reviews = update_gh_meta({"sunpy": old_meta}, {"sunpy": review})

        assert reviews["sunpy"].gh_meta is not None
        assert reviews["sunpy"].gh_meta.stargazers_count == 500

    def test_existing_lookup_is_case_insensitive(self, old_meta):
        """existing_gh_meta keys are lowercased; review keys may not be."""
        review = ReviewModel(
            package_name="SunPy",
            repository_link="https://github.com/sunpy/sunpy",
        )

        reviews = update_gh_meta({"sunpy": old_meta}, {"SunPy": review})

        assert reviews["SunPy"].gh_meta.stargazers_count == 500

    def test_leaves_none_when_nothing_saved(self, review):
        reviews = update_gh_meta({}, {"sunpy": review})

        assert reviews["sunpy"].gh_meta is None

    def test_gap_fills_after_fatal_stop(self, old_meta):
        """Simulate get_metrics stop: both packages None, then merge fills."""
        reviews = {
            "sunpy": ReviewModel(
                package_name="sunpy",
                repository_link="https://github.com/sunpy/sunpy",
            ),
            "other-pkg": ReviewModel(
                package_name="other-pkg",
                repository_link="https://github.com/other/other-pkg",
            ),
        }

        reviews = update_gh_meta({"sunpy": old_meta}, reviews)

        assert reviews["sunpy"].gh_meta.stargazers_count == 500
        assert reviews["other-pkg"].gh_meta is None
