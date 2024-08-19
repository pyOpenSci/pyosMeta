import pickle

import pytest

from pyosmeta.file_io import _list_to_dict, create_paths, load_pickle


@pytest.fixture
def sample_pickle_file(tmp_path):
    data = {"key": "value"}
    file_path = tmp_path / "sample.pkl"
    with open(file_path, "wb") as f:
        pickle.dump(data, f)
    return file_path


def test_load_pickle(sample_pickle_file):
    result = load_pickle(sample_pickle_file)
    assert result == {"key": "value"}


def test_list_to_dict():
    sample_list = [
        {"gh_username": "User1", "data": "value1"},
        {"gh_username": "User2", "data": "value2"},
    ]
    result = _list_to_dict(sample_list, "gh_username")
    expected = {
        "user1": {"gh_username": "User1", "data": "value1"},
        "user2": {"gh_username": "User2", "data": "value2"},
    }
    assert result == expected


def test_create_paths_single_repo():
    repo = "pyos-repo"
    result = create_paths(repo)
    expected = "https://raw.githubusercontent.com/pyOpenSci/pyos-repo/main/.all-contributorsrc"
    assert result == expected


def test_create_paths_multiple_repos():
    repos = ["pyos-repo1", "pyos-repo2"]
    result = create_paths(repos)
    expected = [
        "https://raw.githubusercontent.com/pyOpenSci/pyos-repo1/main/.all-contributorsrc",
        "https://raw.githubusercontent.com/pyOpenSci/pyos-repo2/main/.all-contributorsrc",
    ]
    assert result == expected
