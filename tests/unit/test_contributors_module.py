from unittest.mock import Mock, patch

import pytest

from pyosmeta.contributors import ProcessContributors
from pyosmeta.github_api import GitHubAPI


@pytest.fixture
def github_api_mock():
    return Mock(spec=GitHubAPI)


@pytest.fixture
def json_files():
    return ["https://example.com/file1.json", "https://example.com/file2.json"]


@pytest.fixture
def process_contributors(github_api_mock, json_files):
    return ProcessContributors(github_api_mock, json_files)


def test_check_contrib_type(process_contributors):
    assert (
        process_contributors.check_contrib_type("software-peer-review")
        == "peer-review-guide"
    )
    assert (
        process_contributors.check_contrib_type("python-package-guide")
        == "package-guide"
    )
    assert (
        process_contributors.check_contrib_type("pyopensci.github.io")
        == "web-contrib"
    )
    assert (
        process_contributors.check_contrib_type("pyosMeta") == "code-contrib"
    )
    assert process_contributors.check_contrib_type("other") == "community"


@patch("requests.get")
def test_load_json(mock_get, process_contributors):
    mock_get.return_value.text = '{"key": "value"}'
    result = process_contributors.load_json("https://example.com/test.json")
    assert result == {"key": "value"}


@patch.object(ProcessContributors, "load_json")
def test_process_json_file(mock_load_json, process_contributors):
    mock_load_json.return_value = {
        "contributors": [{"login": "user1"}, {"login": "user2"}]
    }
    contrib_type, users = process_contributors.process_json_file(
        "https://example.com/file1.json"
    )
    assert contrib_type == "community"
    assert users == ["user1", "user2"]


@patch.object(ProcessContributors, "process_json_file")
def test_combine_json_data(mock_process_json_file, process_contributors):
    mock_process_json_file.side_effect = [
        ("type1", ["user1"]),
        ("type2", ["user2"]),
    ]
    combined_data = process_contributors.combine_json_data()
    assert combined_data == {"type1": ["user1"], "type2": ["user2"]}


def test_return_user_info(process_contributors, github_api_mock):
    github_api_mock.get_user_info.return_value = {
        "name": "Test User",
        "location": "Test Location",
        "email": "test@example.com",
        "bio": "Test Bio",
        "twitter_username": "test_twitter",
        "company": "Test Company",
        "blog": "https://test.com",
        "id": 12345,
        "login": "testuser",
    }
    user_info = process_contributors.return_user_info("testuser")
    assert user_info == {
        "name": "Test User",
        "location": "Test Location",
        "email": "test@example.com",
        "bio": "Test Bio",
        "twitter": "test_twitter",
        "mastodon": None,
        "organization": "Test Company",
        "website": "https://test.com",
        "github_image_id": 12345,
        "github_username": "testuser",
    }


def test_update_contrib_type_web_none(process_contributors):
    web_contrib_types = None
    repo_contrib_types = ["type2", "type3"]
    updated_types = process_contributors._update_contrib_type(
        web_contrib_types, repo_contrib_types
    )
    assert updated_types == ["type2", "type3"]


def test_update_contrib_type_new_types(process_contributors):
    web_contrib_types = ["type1"]
    repo_contrib_types = ["type1", "type2", "type3"]
    updated_types = process_contributors._update_contrib_type(
        web_contrib_types, repo_contrib_types
    )
    assert updated_types == ["type1", "type2", "type3"]


def test_update_contrib_type_no_new_types(process_contributors):
    web_contrib_types = ["type1", "type2"]
    repo_contrib_types = ["type1", "type2"]
    updated_types = process_contributors._update_contrib_type(
        web_contrib_types, repo_contrib_types
    )
    assert updated_types == ["type1", "type2"]


def test_update_contrib_type_empty(process_contributors):
    web_contrib_types = []
    repo_contrib_types = []
    updated_types = process_contributors._update_contrib_type(
        web_contrib_types, repo_contrib_types
    )
    assert updated_types == []


def test_update_contrib_type_same_types(process_contributors):
    web_contrib_types = ["type1", "type2"]
    repo_contrib_types = ["type2", "type1"]
    updated_types = process_contributors._update_contrib_type(
        web_contrib_types, repo_contrib_types
    )
    assert updated_types == ["type1", "type2"]


def test_combine_users(process_contributors):
    repo_dict = {
        "user1": {"contributor_type": ["type1"]},
        "user2": {"contributor_type": ["type2"]},
    }
    web_dict = {
        "user1": {"contributor_type": ["type1"]},
        "user3": {"contributor_type": ["type3"]},
    }
    combined_users = process_contributors.combine_users(repo_dict, web_dict)
    assert combined_users == {
        "user1": {"contributor_type": ["type1"]},
        "user3": {"contributor_type": ["type3"]},
        "user2": {"contributor_type": ["type2"]},
    }
