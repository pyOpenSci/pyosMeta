"""Fetch GitHub editorial teams and write website roster YAML.

Writes ``editorial-board.yml``, ``emeritus-editors.yml``, and updates
editorial flags/titles in ``contributors.yml`` in ``--data-dir``.

To run: update-editorial-board --data-dir /path/to/website/data
"""

import argparse
from pathlib import Path

from ruamel.yaml import YAML

from pyosmeta.constants import (
    CONTRIBUTORS_FILE,
    CONTRIBUTORS_RAW_URL,
    EDITORIAL_BOARD_FILE,
    EDITORIAL_BOARD_RAW_URL,
    EDITORIAL_TEAMS,
    EMERITUS_EDITORS_FILE,
    EMERITUS_EDITORS_RAW_URL,
)
from pyosmeta.contributors import ProcessContributors
from pyosmeta.editorial import (
    apply_roster_to_contributors,
    board_yaml,
    build_roster,
    emeritus_yaml,
)
from pyosmeta.file_io import (
    clean_export_yml,
    get_output_path,
    open_yml_file,
)
from pyosmeta.github_api import GitHubAPI
from pyosmeta.logging import logger


def _load_yaml(path: Path | None, url: str):
    """Load YAML from a local file if it exists, otherwise from ``url``."""
    if path and path.exists():
        with path.open() as handle:
            yaml = YAML(typ="safe", pure=True)
            return yaml.load(handle)
    return open_yml_file(url)


def _write_mapping_yaml(path: Path, data: dict) -> None:
    """Write a username-keyed mapping with 2-space indent."""
    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with path.open("w") as handle:
        yaml.dump(data, handle)


def _flag_labels(entry: dict) -> str:
    labels = []
    if entry["peer_review_lead"]:
        labels.append("peer_review_lead")
    if entry["eic_team"]:
        labels.append("eic_team")
    if entry["emeritus_peer_review_lead"]:
        labels.append("emeritus_peer_review_lead")
    if entry["emeritus_eic"]:
        labels.append("emeritus_eic")
    return f"  {' '.join(labels)}" if labels else ""


def _print_roster(roster: dict[str, dict]) -> None:
    active = sorted(name for name, row in roster.items() if row["active"])
    emeritus = sorted(
        name for name, row in roster.items() if not row["active"]
    )
    print(f"\nActive editors ({len(active)}):")
    for name in active:
        print(f"  {name}{_flag_labels(roster[name])}")
    print(f"\nEmeritus editors ({len(emeritus)}):")
    for name in emeritus:
        print(f"  {name}{_flag_labels(roster[name])}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Update editorial board YAML from GitHub org team membership."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help=(
            "Directory containing the website YAML files "
            "(editorial-board.yml, emeritus-editors.yml, "
            "contributors.yml). Defaults to data/ (relative to the "
            "current working directory)."
        ),
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    board_path = data_dir / EDITORIAL_BOARD_FILE
    emeritus_path = data_dir / EMERITUS_EDITORS_FILE
    contrib_path = data_dir / CONTRIBUTORS_FILE

    github_api = GitHubAPI()
    teams: dict[str, list[str]] = {}
    for key, slug in EDITORIAL_TEAMS.items():
        members = github_api.get_team_members(slug)
        teams[key] = members
        print(f"{key} ({slug}): {len(members)}")
        for login in sorted(member.lower() for member in members):
            print(f"  {login}")

    previous = {}
    board_existing = _load_yaml(board_path, EDITORIAL_BOARD_RAW_URL)
    emeritus_existing = _load_yaml(emeritus_path, EMERITUS_EDITORS_RAW_URL)
    if isinstance(emeritus_existing, dict):
        previous.update(emeritus_existing)
    if isinstance(board_existing, dict):
        previous.update(board_existing)

    roster = build_roster(teams, previous)
    _print_roster(roster)

    # Resolve OS-safe write targets (creates data_dir if needed).
    board_path = get_output_path(data_dir, EDITORIAL_BOARD_FILE)
    emeritus_path = get_output_path(data_dir, EMERITUS_EDITORS_FILE)
    contrib_path = get_output_path(data_dir, CONTRIBUTORS_FILE)

    _write_mapping_yaml(board_path, board_yaml(roster))
    _write_mapping_yaml(emeritus_path, emeritus_yaml(roster))
    print(f"\nWrote {board_path}")
    print(f"Wrote {emeritus_path}")

    contribs = _load_yaml(contrib_path, CONTRIBUTORS_RAW_URL)
    if not isinstance(contribs, list):
        logger.error(
            "Could not load contributors.yml as a list; skipping "
            "contributor flag updates."
        )
        return

    processor = ProcessContributors(github_api, [])
    apply_roster_to_contributors(contribs, roster, processor.return_user_info)
    clean_export_yml(contribs, contrib_path)
    print(f"Wrote {contrib_path}")


if __name__ == "__main__":
    main()
