from pyosmeta.contributors import ProcessContributors
from pyosmeta.github_api import GitHubAPI


def test_init(mocker):
    """Test that the ProcessContributors object instantiates as
    expected"""

    # Create a mock GitHubAPI object
    github_api_mock = mocker.MagicMock(spec=GitHubAPI)
    json_files = ["file1.json", "file2.json"]

    process_contributors = ProcessContributors(github_api_mock, json_files)

    assert process_contributors.github_api == github_api_mock
    assert process_contributors.json_files == json_files


def test_return_user_info(mock_github_api, ghuser_response):
    """Test that return from github API user info returns expected
    GH username."""

    process_contributors = ProcessContributors(mock_github_api, [])
    gh_handle = "chayadecacao"
    user_info = process_contributors.return_user_info(gh_handle)

    assert user_info["github_username"] == gh_handle
