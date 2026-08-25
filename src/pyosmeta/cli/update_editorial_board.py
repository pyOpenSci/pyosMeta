"""Fetch GitHub editorial teams and write website roster YAML.

Writes ``editorial-board.yml``, ``emeritus-editors.yml``, and updates
editorial flags/titles in ``contributors.yml`` in the ``data/`` directory
relative to the current working directory.

To run (from the website repo root): update-editorial-board
"""

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
    MANUAL_EDITORIAL_ROSTER_FILE,
)
from pyosmeta.contributors import ProcessContributors
from pyosmeta.editorial import (
    RosterEntry,
    apply_roster_to_contributors,
    board_yaml,
    build_roster,
    emeritus_yaml,
    merge_manual_roster,
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


def _flag_labels(entry: RosterEntry) -> str:
    labels = []
    if entry.active_peer_review_lead:
        labels.append("peer_review_lead")
    if entry.active_eic:
        labels.append("eic")
    if entry.active_triage:
        labels.append("triage")
    if entry.emeritus_peer_review_lead:
        labels.append("emeritus_peer_review_lead")
    if entry.emeritus_eic:
        labels.append("emeritus_eic")
    if entry.emeritus_triage:
        labels.append("emeritus_triage")
    return f"  {' '.join(labels)}" if labels else ""


def _print_roster(roster: dict[str, RosterEntry]) -> None:
    active = sorted(name for name, row in roster.items() if row.is_active)
    emeritus = sorted(
        name for name, row in roster.items() if not row.is_active
    )
    print(f"\nActive editors ({len(active)}):")
    for name in active:
        print(f"  {name}{_flag_labels(roster[name])}")
    print(f"\nEmeritus editors ({len(emeritus)}):")
    for name in emeritus:
        print(f"  {name}{_flag_labels(roster[name])}")


def main() -> None:
    # The website YAML lives in data/ relative to the current working
    # directory (run from the pyopensci.github.io repo root).
    data_dir = Path("data")
    # Resolve OS-safe paths once (creates data_dir if needed); reused for
    # both reading the existing YAML and writing the regenerated files.
    board_path = get_output_path(data_dir, EDITORIAL_BOARD_FILE)
    emeritus_path = get_output_path(data_dir, EMERITUS_EDITORS_FILE)
    contrib_path = get_output_path(data_dir, CONTRIBUTORS_FILE)
    manual_path = data_dir / MANUAL_EDITORIAL_ROSTER_FILE

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

    manual = {}
    if manual_path.exists():
        with manual_path.open() as handle:
            loaded = YAML(typ="safe", pure=True).load(handle)
        if isinstance(loaded, dict):
            manual = loaded
            print(f"\nManual roster ({manual_path}): {len(manual)}")
            for login in sorted(manual):
                print(f"  {login}")
        else:
            logger.warning(
                "%s did not parse as a mapping; ignoring.", manual_path
            )
    else:
        print(f"\nNo {MANUAL_EDITORIAL_ROSTER_FILE}; skipping manual merge.")

    roster = merge_manual_roster(roster, manual)
    _print_roster(roster)

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
