import pytest

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
    def test_uses_fresh_data_when_fetch_succeeds(
        self, mocker, review, endpoints, new_meta, old_meta
    ):
        """A successful fetch should update gh_meta, even if we had
        previously saved metrics for this package."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api, "get_repo_meta_github", return_value=new_meta
        )

        reviews = github_api.get_metrics(
            endpoints, {"sunpy": review}, {"sunpy": old_meta}
        )

        assert reviews["sunpy"].gh_meta.stargazers_count == 999

    def test_keeps_previous_data_when_fetch_fails(
        self, mocker, review, endpoints, old_meta
    ):
        """If the API call fails (returns None), we must never delete
        previously collected metrics."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api, "get_repo_meta_github", return_value=None
        )

        reviews = github_api.get_metrics(
            endpoints, {"sunpy": review}, {"sunpy": old_meta}
        )

        assert reviews["sunpy"].gh_meta is not None
        assert reviews["sunpy"].gh_meta.stargazers_count == 500

    def test_existing_gh_meta_lookup_is_case_insensitive(
        self, mocker, review, endpoints, old_meta
    ):
        """existing_gh_meta is keyed by lowercased package name (as
        produced by file_io.load_website_yml), so lookups must lowercase
        the package name too."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api, "get_repo_meta_github", return_value=None
        )

        reviews = github_api.get_metrics(
            endpoints, {"sunpy": review}, {"SunPy".lower(): old_meta}
        )

        assert reviews["sunpy"].gh_meta.stargazers_count == 500

    def test_no_data_when_fetch_fails_and_nothing_saved(
        self, mocker, review, endpoints
    ):
        """If we've never successfully fetched metrics for a package and
        the fetch fails, gh_meta should stay empty (nothing to lose)."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api, "get_repo_meta_github", return_value=None
        )

        reviews = github_api.get_metrics(endpoints, {"sunpy": review}, {})

        assert reviews["sunpy"].gh_meta is None

    def test_unexpected_exception_does_not_stop_the_batch(
        self, mocker, review, endpoints, old_meta
    ):
        """An unexpected exception (e.g. a network error) from
        get_repo_meta_github for one package must not crash the batch -
        it should be treated like a failed fetch, falling back to
        previously saved metrics."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api,
            "get_repo_meta_github",
            side_effect=RuntimeError("boom"),
        )

        reviews = github_api.get_metrics(
            endpoints, {"sunpy": review}, {"sunpy": old_meta}
        )

        assert reviews["sunpy"].gh_meta is not None
        assert reviews["sunpy"].gh_meta.stargazers_count == 500

    def test_fatal_error_falls_back_for_current_package(
        self, mocker, review, endpoints, old_meta
    ):
        """A GitHubAPIError (401 or rate-limit-exhausted 403) for a
        package must not crash the batch - it should fall back to
        previously saved metrics, just like any other failed fetch."""
        github_api = GitHubAPI()
        mocker.patch.object(
            github_api,
            "get_repo_meta_github",
            side_effect=GitHubAPIError("401 Unauthorized"),
        )

        reviews = github_api.get_metrics(
            endpoints, {"sunpy": review}, {"sunpy": old_meta}
        )

        assert reviews["sunpy"].gh_meta is not None
        assert reviews["sunpy"].gh_meta.stargazers_count == 500

    def test_fatal_error_stops_remaining_packages_from_being_fetched(
        self, mocker, old_meta
    ):
        """Once a GitHubAPIError occurs, no further API calls should be
        made for remaining packages - they should go straight to fallback
        (or stay empty if nothing was saved)."""
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

        reviews = github_api.get_metrics(
            endpoints, reviews_input, {"sunpy": old_meta}
        )

        mock_fetch.assert_called_once()
        assert reviews["sunpy"].gh_meta.stargazers_count == 500
        assert reviews["other-pkg"].gh_meta is None

    def test_skips_non_github_hosts(self, mocker, endpoints, old_meta):
        """Non-GitHub repos should be skipped without touching gh_meta."""
        review = ReviewModel(
            package_name="example",
            repository_link="https://gitlab.com/example/example",
        )
        github_api = GitHubAPI()
        mock_fetch = mocker.patch.object(github_api, "get_repo_meta_github")

        reviews = github_api.get_metrics(
            {"example": {"owner": "example", "repo_name": "example"}},
            {"example": review},
            {"example": old_meta},
        )

        mock_fetch.assert_not_called()
        assert reviews["example"].gh_meta is None
