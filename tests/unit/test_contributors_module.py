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
