import os
import secrets

import pytest

from pyosmeta import github_api
from pyosmeta.github_api import GitHubAPI


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
