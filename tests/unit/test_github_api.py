import os

import pytest
import secrets

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


def test_get_token(mock_github_token):
    """Test that get_token accesses the token correctly when it is
    present."""
    github_api = GitHubAPI()
    token = github_api.get_token()

    assert token == os.environ["GITHUB_TOKEN"]


def test_missing_token(mock_missing_github_token, tmpdir):
    """Test that a keyerror is raised when the token is missing."""
    os.chdir(tmpdir)
    github_api = GitHubAPI()

    with pytest.raises(KeyError, match="Oops! A GITHUB_TOKEN environment"):
        github_api.get_token()


def test_api_endpoint(github_api):
    """Test that the generated api url created in the property
    is as expected
    """
    expected_endpoint = (
        "https://api.github.com/repos/pyopensci/pyosmeta/"
        "issues?labels=label1,label2&state=all&per_page=100"
    )
    assert github_api.api_endpoint == expected_endpoint
