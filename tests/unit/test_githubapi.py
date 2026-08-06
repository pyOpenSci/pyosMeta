import logging
import os
import secrets

import pytest

from pyosmeta import github_api
from pyosmeta.github_api import GitHubAPI
from pyosmeta.models.base import GhMeta


@pytest.fixture
def mock_github_token(monkeypatch):
    """Fixture to create a mock token - i don't believe this
    is working as expected either."""
    # Generate a random token
    random_token = secrets.token_hex(16)

    # Mocking the GitHub token in the environment variable
    monkeypatch.setenv("GITHUB_TOKEN", random_token)


@pytest.fixture
def mock_missing_github_token(monkeypatch, tmpdir):
    os.chdir(tmpdir)
    # Remove the GitHub token from the environment variable
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def do_nothing():
        pass

    monkeypatch.setattr(github_api, "load_dotenv", do_nothing)


def test_get_token(mock_github_token):
    """Test that get_token accesses the token correctly when it is
    present."""
    github_api = GitHubAPI()
    token = github_api.get_token()

    assert token == os.environ["GITHUB_TOKEN"]


def test_missing_token(mock_missing_github_token, tmpdir):
    """Test that a keyerror is raised when the token is missing.."""

    github_api = GitHubAPI()

    with pytest.raises(KeyError, match="Oops! A GITHUB_TOKEN environment"):
        github_api.get_token()


@pytest.mark.parametrize(
    "org, repo, endpoint_type, labels, expected_url",
    [
        (
            "pyopensci",
            "pyosmeta",
            "issues",
            [],
            "https://api.github.com/repos/pyopensci/pyosmeta/issues?state=all&per_page=100",
        ),
        (
            "pyopensci",
            "pyosmeta",
            "issues",
            ["label1"],
            "https://api.github.com/repos/pyopensci/pyosmeta/issues?state=all&per_page=100&labels=label1",
        ),
        (
            "pyopensci",
            "pyosmeta",
            "issues",
            ["label1", "label2"],
            "https://api.github.com/repos/pyopensci/pyosmeta/issues?state=all&per_page=100",
        ),
        (
            "pyopensci",
            "pyosmeta",
            "pulls",
            [],
            "https://api.github.com/repos/pyopensci/pyosmeta/pulls?state=all&per_page=100",
        ),
        (
            "pyopensci",
            "pyosmeta",
            "pulls",
            ["label1"],
            "https://api.github.com/repos/pyopensci/pyosmeta/pulls?state=all&per_page=100&labels=label1",
        ),
        (
            "pyopensci",
            "pyosmeta",
            "pulls",
            ["label1", "label2"],
            "https://api.github.com/repos/pyopensci/pyosmeta/pulls?state=all&per_page=100",
        ),
    ],
)
def test_api_endpoint(org, repo, endpoint_type, labels, expected_url):
    """Test that the generated API URL created in the property is valid."""
    github_api = GitHubAPI()
    github_api.org = org
    github_api.repo = repo
    github_api.endpoint_type = endpoint_type
    github_api.labels = labels

    assert github_api.api_endpoint == expected_url


@pytest.mark.parametrize(
    "after_date, expected_url",
    [
        (
            "2023-13-01",  # Invalid month
            None,
        ),
        (
            "2023-10-32",  # Invalid day
            None,
        ),
        (
            "2023-10",  # Incomplete date
            None,
        ),
        (
            "invalid-date",  # Invalid format
            None,
        ),
        (
            "2024-08-16",  # Valid date
            "https://api.github.com/repos/org/repo/issues?state=all&per_page=100&since=2024-08-16",
        ),
    ],
)
def test_api_endpoint_with_invalid_dates(after_date, expected_url):
    """Test that a URL generated with valid or invalid dates works as expected"""
    github_api = GitHubAPI(
        org="org", repo="repo", endpoint_type="issues", after_date=after_date
    )

    if expected_url is None:
        with pytest.raises(ValueError, match="Invalid after date"):
            github_api.api_endpoint
    else:
        assert github_api.api_endpoint == expected_url


def test_get_user_info_successful(mocker, ghuser_response):
    """Test that an expected response returns properly"""

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = ghuser_response
    mocker.patch("requests.get", return_value=mock_response)

    github_api_instance = GitHubAPI()
    user_info = github_api_instance.get_user_info("example_user")

    assert user_info == ghuser_response


def test_get_user_info_bad_credentials(mocker):
    """Test that a value error is raised when the GH token is not
    valid."""

    mock_response = mocker.Mock()
    mock_response.status_code = 401
    mocker.patch("requests.get", return_value=mock_response)

    github_api = GitHubAPI()

    with pytest.raises(ValueError, match="Oops, I couldn't authenticate"):
        github_api.get_user_info("example_user")


def test_gh_meta_field_mapping_matches_model_fields():
    """Ensure GhMeta field mapping stays aligned with the model.

    This test makes sure that all required GhMeta fields are accounted for and
    that non-contributor fields have an explicit REST source mapping.
    """
    mapping = GitHubAPI.get_gh_meta_field_mapping()

    required_fields = set(mapping["required_fields"])
    model_fields = set(GhMeta.model_fields.keys())
    mapped_fields = set(mapping["rest_field_map"].keys())

    assert required_fields == model_fields
    assert required_fields == mapped_fields.union({"contrib_count"})
    assert mapping["last_commit_source"] == "pushed_at"
    assert (
        mapping["contrib_source"] == "GET /repos/{owner}/{repo}/contributors"
    )


@pytest.fixture
def rest_repo_response():
    """A representative GET /repos/{owner}/{repo} payload."""
    return {
        "name": "pyosmeta",
        "description": "A package for pyOS metadata.",
        "homepage": "https://example.com/docs",
        "created_at": "2020-01-01T00:00:00Z",
        "stargazers_count": 42,
        "watchers_count": 42,
        "open_issues_count": 3,
        "forks_count": 5,
        "pushed_at": "2024-06-01T00:00:00Z",
    }


def test_get_metrics_rest_successful(mocker, rest_repo_response):
    """Test that a 200 response is normalized to GhMeta-compatible keys."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = rest_repo_response
    mocker.patch("requests.get", return_value=mock_response)

    github_api = GitHubAPI()
    metrics = github_api._get_metrics_rest(
        {"owner": "pyopensci", "repo_name": "pyosmeta"}
    )

    assert metrics == {
        "name": "pyosmeta",
        "description": "A package for pyOS metadata.",
        "documentation": "https://example.com/docs",
        "created_at": "2020-01-01T00:00:00Z",
        "stargazers_count": 42,
        "watchers_count": 42,
        "open_issues_count": 3,
        "forks_count": 5,
        "last_commit": "2024-06-01T00:00:00Z",
    }


def test_get_metrics_rest_normalizes_empty_homepage(
    mocker, rest_repo_response
):
    """Test that an empty-string homepage is normalized to None."""
    rest_repo_response["homepage"] = ""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = rest_repo_response
    mocker.patch("requests.get", return_value=mock_response)

    github_api = GitHubAPI()
    metrics = github_api._get_metrics_rest(
        {"owner": "pyopensci", "repo_name": "pyosmeta"}
    )

    assert metrics["documentation"] is None


def test_get_metrics_rest_not_found(mocker, caplog):
    """Test that a 404 response returns None and logs a warning."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mocker.patch("requests.get", return_value=mock_response)

    github_api = GitHubAPI()

    with caplog.at_level(logging.WARNING):
        metrics = github_api._get_metrics_rest(
            {"owner": "pyopensci", "repo_name": "missing-repo"}
        )

    assert metrics is None
    assert "Repository not found" in caplog.text


def test_get_metrics_rest_forbidden(mocker, caplog):
    """Test that a 403 response returns None and logs a warning."""
    mock_response = mocker.Mock()
    mock_response.status_code = 403
    mock_response.text = "rate limited"
    mock_response.headers = {}
    mocker.patch("requests.get", return_value=mock_response)

    github_api = GitHubAPI()

    with caplog.at_level(logging.WARNING):
        metrics = github_api._get_metrics_rest(
            {"owner": "pyopensci", "repo_name": "pyosmeta"}
        )

    assert metrics is None
    assert "API limit" in caplog.text


def test_get_metrics_rest_unexpected_error(mocker, caplog):
    """Test that an unexpected status code returns None and logs a warning."""
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mocker.patch("requests.get", return_value=mock_response)

    github_api = GitHubAPI()

    with caplog.at_level(logging.WARNING):
        metrics = github_api._get_metrics_rest(
            {"owner": "pyopensci", "repo_name": "pyosmeta"}
        )

    assert metrics is None
    assert "Unexpected HTTP error" in caplog.text


def test_get_repo_meta_github_is_rest_first(mocker):
    """Test that get_repo_meta_github uses REST for metadata (not GraphQL)
    and merges in contrib_count from the separate contributors call."""
    github_api = GitHubAPI()
    rest_metrics = {
        "name": "pyosmeta",
        "description": "A package for pyOS metadata.",
        "documentation": None,
        "created_at": "2020-01-01T00:00:00Z",
        "stargazers_count": 42,
        "watchers_count": 42,
        "open_issues_count": 3,
        "forks_count": 5,
        "last_commit": "2024-06-01T00:00:00Z",
    }
    mock_rest = mocker.patch.object(
        github_api, "_get_metrics_rest", return_value=dict(rest_metrics)
    )
    mock_graphql = mocker.patch.object(github_api, "_get_metrics_graphql")
    mock_contrib = mocker.patch.object(
        github_api, "_get_contrib_count_rest", return_value=7
    )

    metrics = github_api.get_repo_meta_github(
        {"owner": "pyopensci", "repo_name": "pyosmeta"}
    )

    mock_rest.assert_called_once_with(
        {"owner": "pyopensci", "repo_name": "pyosmeta"}
    )
    mock_graphql.assert_not_called()
    mock_contrib.assert_called_once_with(
        {"owner": "pyopensci", "repo_name": "pyosmeta"}
    )
    assert metrics == {**rest_metrics, "contrib_count": 7}


def test_get_repo_meta_github_returns_none_when_rest_fails(mocker):
    """Test that a failed REST fetch returns None without calling the
    contributors endpoint."""
    github_api = GitHubAPI()
    mocker.patch.object(github_api, "_get_metrics_rest", return_value=None)
    mock_contrib = mocker.patch.object(github_api, "_get_contrib_count_rest")

    metrics = github_api.get_repo_meta_github(
        {"owner": "pyopensci", "repo_name": "pyosmeta"}
    )

    assert metrics is None
    mock_contrib.assert_not_called()
