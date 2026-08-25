"""Tests for editorial roster building and contributor flag sync."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from ruamel.yaml import YAML

from pyosmeta.cli import update_editorial_board
from pyosmeta.editorial import (
    RosterEntry,
    apply_roster_to_contributors,
    board_yaml,
    build_roster,
    emeritus_yaml,
)

_ROLE_ATTRS = (
    "active_editor",
    "active_eic",
    "active_peer_review_lead",
    "emeritus_editor",
    "is_active",
)


def _teams(**overrides):
    base = {
        "editorial_board": [],
        "emeritus_editors": [],
        "eic_team": [],
        "peer_review_lead": [],
    }
    base.update(overrides)
    return base


@pytest.mark.parametrize(
    "teams, username, true_attrs",
    [
        (
            _teams(editorial_board=["alice"]),
            "alice",
            {"active_editor", "is_active"},
        ),
        (_teams(eic_team=["bob"]), "bob", {"active_eic", "is_active"}),
        (
            _teams(peer_review_lead=["carol"]),
            "carol",
            {"active_peer_review_lead", "is_active"},
        ),
        (_teams(emeritus_editors=["dave"]), "dave", {"emeritus_editor"}),
        # Active membership wins over emeritus team membership
        (
            _teams(editorial_board=["lwasser"], emeritus_editors=["lwasser"]),
            "lwasser",
            {"active_editor", "is_active"},
        ),
    ],
)
def test_build_roster_role_flags(teams, username, true_attrs):
    entry = build_roster(teams)[username]
    for attr in _ROLE_ATTRS:
        assert getattr(entry, attr) is (attr in true_attrs)


@pytest.mark.parametrize(
    "previous, teams, username, expected_eic, expected_pr_lead",
    [
        (
            {"cmarmo": {"emeritus_eic": True}},
            _teams(emeritus_editors=["cmarmo"]),
            "cmarmo",
            True,
            False,
        ),
        (
            {"oldlead": {"emeritus_peer_review_lead": True}},
            _teams(emeritus_editors=["oldlead"]),
            "oldlead",
            False,
            True,
        ),
        # Historical flags survive even when the person is active
        (
            {"alice": {"emeritus_eic": True}},
            _teams(editorial_board=["alice"]),
            "alice",
            True,
            False,
        ),
        # previous keys are case-normalized for lookup
        (
            {"CMARMO": {"emeritus_eic": True}},
            _teams(emeritus_editors=["Cmarmo"]),
            "cmarmo",
            True,
            False,
        ),
    ],
)
def test_build_roster_preserves_historical_flags(
    previous, teams, username, expected_eic, expected_pr_lead
):
    entry = build_roster(teams, previous=previous)[username]
    assert entry.emeritus_eic is expected_eic
    assert entry.emeritus_peer_review_lead is expected_pr_lead


def test_build_roster_normalizes_username_case():
    roster = build_roster(
        _teams(
            editorial_board=["Alice"],
            emeritus_editors=["DAVE"],
            eic_team=["BoB"],
        )
    )
    assert set(roster) == {"alice", "dave", "bob"}


def test_active_over_emeritus_yaml_split():
    roster = build_roster(
        _teams(editorial_board=["lwasser"], emeritus_editors=["lwasser"])
    )
    assert "lwasser" in board_yaml(roster)
    assert "lwasser" not in emeritus_yaml(roster)


@pytest.mark.parametrize(
    "person, roster, expected_board, expected_emeritus, expected_title",
    [
        (
            {
                "github_username": "alice",
                "editorial_board": False,
                "emeritus_editor": False,
                "contributor_type": ["community"],
                "title": None,
            },
            {"alice": RosterEntry(active_editor=True)},
            True,
            False,
            "Editor",
        ),
        (
            {
                "github_username": "dave",
                "editorial_board": True,
                "emeritus_editor": False,
                "contributor_type": ["editor"],
                "title": "Editor",
            },
            {"dave": RosterEntry(emeritus_editor=True)},
            False,
            True,
            "Emeritus Editor",
        ),
        # Guard: emeritus not on any team keeps emeritus_editor
        (
            {
                "github_username": "ghost",
                "editorial_board": False,
                "emeritus_editor": True,
                "title": "Emeritus Editor",
            },
            {},
            False,
            True,
            "Emeritus Editor",
        ),
        # Non-roster, non-emeritus: flags cleared
        (
            {
                "github_username": "other",
                "editorial_board": True,
                "emeritus_editor": False,
                "title": "Editor",
            },
            {},
            False,
            False,
            None,
        ),
    ],
)
def test_apply_roster_to_existing_people(
    person, roster, expected_board, expected_emeritus, expected_title
):
    contribs = [person]
    apply_roster_to_contributors(contribs, roster)
    assert contribs[0]["editorial_board"] is expected_board
    assert contribs[0]["emeritus_editor"] is expected_emeritus
    assert contribs[0]["title"] == expected_title
    if expected_board:
        assert "editor" in [t.lower() for t in contribs[0]["contributor_type"]]


def test_apply_roster_appends_new_team_member_stub():
    contribs: list[dict] = []
    roster = {"newbie": RosterEntry(active_editor=True, active_eic=True)}

    def fetch_user(username: str) -> dict:
        return {
            "github_username": username,
            "github_image_id": 99,
            "name": "New Editor",
        }

    apply_roster_to_contributors(contribs, roster, fetch_user)
    stub = contribs[0]
    assert stub["github_username"] == "newbie"
    assert stub["name"] == "New Editor"
    assert stub["editorial_board"] is True
    assert stub["contributor_type"] == ["editor"]
    titles = (
        stub["title"] if isinstance(stub["title"], list) else [stub["title"]]
    )
    assert "Editor in Chief" in titles


def _dump_yaml(path: Path, data) -> None:
    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    with path.open("w") as handle:
        yaml.dump(data, handle)


def _load_yaml(path: Path):
    yaml = YAML(typ="safe", pure=True)
    with path.open() as handle:
        return yaml.load(handle)


@pytest.fixture
def editorial_cli_data_dir(tmp_path, monkeypatch):
    """Run update_editorial_board.main against a temp data/ tree."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _dump_yaml(
        data_dir / "editorial-board.yml",
        {
            "alice": {
                "peer_review_lead": False,
                "eic_team": False,
                "emeritus_peer_review_lead": False,
                "emeritus_eic": False,
            }
        },
    )
    _dump_yaml(
        data_dir / "emeritus-editors.yml",
        {
            "cmarmo": {
                "emeritus_peer_review_lead": False,
                "emeritus_eic": True,
            }
        },
    )
    _dump_yaml(
        data_dir / "contributors.yml",
        [
            {
                "github_username": "alice",
                "name": "Alice",
                "editorial_board": True,
                "emeritus_editor": False,
                "contributor_type": ["editor"],
                "title": "Editor",
            },
            {
                "github_username": "ghost",
                "name": "Ghost Emeritus",
                "editorial_board": False,
                "emeritus_editor": True,
                "contributor_type": ["editor"],
                "title": "Emeritus Editor",
            },
            {
                "github_username": "cmarmo",
                "name": "Chiara",
                "editorial_board": False,
                "emeritus_editor": True,
                "contributor_type": ["editor"],
                "title": "Emeritus Editor in Chief",
            },
        ],
    )

    team_members = {
        "editorial-board": ["alice", "newbie"],
        "emeritus-editors": ["cmarmo"],
        "eic-team": [],
        "peer-review-lead": ["alice"],
    }
    mock_api = Mock()
    mock_api.get_team_members.side_effect = lambda slug: team_members[slug]
    monkeypatch.setattr(update_editorial_board, "GitHubAPI", lambda: mock_api)

    mock_processor = Mock()
    mock_processor.return_user_info.return_value = {
        "github_username": "newbie",
        "github_image_id": 1,
        "name": "New Editor",
    }
    monkeypatch.setattr(
        update_editorial_board,
        "ProcessContributors",
        lambda *args, **kwargs: mock_processor,
    )

    monkeypatch.chdir(tmp_path)
    update_editorial_board.main()
    return data_dir


def test_cli_writes_board_and_emeritus_yaml(editorial_cli_data_dir):
    board = _load_yaml(editorial_cli_data_dir / "editorial-board.yml")
    emeritus = _load_yaml(editorial_cli_data_dir / "emeritus-editors.yml")

    assert board["alice"]["peer_review_lead"] is True
    assert "newbie" in board
    assert emeritus["cmarmo"]["emeritus_eic"] is True


def test_cli_updates_contributors_flags(editorial_cli_data_dir):
    by_user = {
        row["github_username"]: row
        for row in _load_yaml(editorial_cli_data_dir / "contributors.yml")
    }

    assert by_user["alice"]["editorial_board"] is True
    assert by_user["alice"]["emeritus_editor"] is False
    assert by_user["cmarmo"]["emeritus_editor"] is True
    # Guard: not on any team, still emeritus
    assert by_user["ghost"]["emeritus_editor"] is True
    assert by_user["ghost"]["editorial_board"] is False
    assert by_user["newbie"]["editorial_board"] is True
    assert "editor" in [
        t.lower() for t in by_user["newbie"]["contributor_type"]
    ]
