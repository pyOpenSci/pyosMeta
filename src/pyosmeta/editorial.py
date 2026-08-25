"""Build the editor roster from GitHub org team membership.

GitHub teams are the source of truth for active and emeritus specialty
roles (``eic-team``, ``triage-team``, ``emeritus-editor-in-chief``,
``emeritus-peer-review-lead``, ``emeritus-triage-team``,
``emeritus-editors``).

People who cannot join org teams are listed in
``manual-editorial-roster.yml`` and merged after the team fetch via
``merge_manual_roster``.
"""

from dataclasses import dataclass
from typing import Any, Callable

# Manual YAML keys (only ``true`` values needed) → RosterEntry fields.
_MANUAL_FLAG_MAP = {
    "editor": "active_editor",
    "eic": "active_eic",
    "peer_review_lead": "active_peer_review_lead",
    "triage": "active_triage",
    "emeritus_editor": "emeritus_editor",
    "emeritus_eic": "emeritus_eic",
    "emeritus_peer_review_lead": "emeritus_peer_review_lead",
    "emeritus_triage": "emeritus_triage",
}


@dataclass
class RosterEntry:
    """Role flags for one editor, derived from GitHub team membership.

    A person is *active* when they hold any live active role
    (``is_active``): ``editorial-board``, ``peer-review-lead``,
    ``eic-team``, or ``triage-team``. ``emeritus_editor`` means they are
    on the ``emeritus-editors`` team and hold no active role.
    ``emeritus_peer_review_lead``, ``emeritus_eic``, and
    ``emeritus_triage`` come from the matching emeritus GitHub teams.
    """

    active_editor: bool = False
    active_peer_review_lead: bool = False
    active_eic: bool = False
    active_triage: bool = False
    emeritus_editor: bool = False
    emeritus_peer_review_lead: bool = False
    emeritus_eic: bool = False
    emeritus_triage: bool = False

    @property
    def is_active(self) -> bool:
        """True when the person holds any active editorial role."""
        return (
            self.active_editor
            or self.active_peer_review_lead
            or self.active_eic
            or self.active_triage
        )


EDITORIAL_TITLE_STRINGS = frozenset(
    {
        "Editor",
        "Editor in Chief",
        "Peer Review Lead",
        "Peer Review Triage",
        "Peer review triage",  # legacy casing in contributors.yml
        "Emeritus Editor",
        "Emeritus Editor in Chief",
        "Emeritus Peer Review Lead",
        "Emeritus Peer Review Triage",
    }
)


def _usernames(logins: list[str] | None) -> set[str]:
    return {
        (login or "").strip().lower()
        for login in (logins or [])
        if (login or "").strip()
    }


def build_roster(
    teams: dict[str, list[str]],
    previous: dict[str, dict] | None = None,
) -> dict[str, RosterEntry]:
    """Return username -> role flags from team membership.

    Parameters
    ----------
    teams : dict
        Mapping of ``EDITORIAL_TEAMS`` keys to GitHub logins.
    previous : dict, optional
        Ignored. Kept so callers can pass existing board YAML without
        breaking; emeritus specialty flags come from GitHub teams.
    """
    _ = previous
    board = _usernames(teams.get("editorial_board"))
    emeritus = _usernames(teams.get("emeritus_editors"))
    eic = _usernames(teams.get("eic_team"))
    pr_lead = _usernames(teams.get("peer_review_lead"))
    triage = _usernames(teams.get("triage_team"))
    emeritus_eic = _usernames(teams.get("emeritus_eic"))
    emeritus_pr_lead = _usernames(teams.get("emeritus_peer_review_lead"))
    emeritus_triage = _usernames(teams.get("emeritus_triage"))

    active = board | eic | pr_lead | triage
    emeritus_only = emeritus - active

    roster: dict[str, RosterEntry] = {}
    for username in active | emeritus_only:
        roster[username] = RosterEntry(
            active_editor=username in board,
            active_peer_review_lead=username in pr_lead,
            active_eic=username in eic,
            active_triage=username in triage,
            emeritus_editor=username in emeritus_only,
            emeritus_peer_review_lead=username in emeritus_pr_lead,
            emeritus_eic=username in emeritus_eic,
            emeritus_triage=username in emeritus_triage,
        )
    return roster


def merge_manual_roster(
    roster: dict[str, RosterEntry],
    manual: dict[str, dict] | None,
) -> dict[str, RosterEntry]:
    """Add hand-maintained people who are not on GitHub teams.

    ``manual`` is the mapping from ``manual-editorial-roster.yml``. Only
    role keys set to true are applied (``editor``, ``emeritus_editor``,
    specialty flags). ``name`` / ``note`` are ignored here.

    If a username is already in ``roster`` from team membership, the
    team entry wins and the manual row is skipped.
    """
    if not manual:
        return roster

    out = dict(roster)
    for raw_name, raw_flags in manual.items():
        username = (raw_name or "").strip().lower()
        if not username or username in out:
            continue
        if not isinstance(raw_flags, dict):
            continue

        kwargs: dict[str, bool] = {}
        for yaml_key, attr in _MANUAL_FLAG_MAP.items():
            if raw_flags.get(yaml_key) is True:
                kwargs[attr] = True
        if not kwargs:
            continue
        out[username] = RosterEntry(**kwargs)
    return out


def board_yaml(roster: dict[str, RosterEntry]) -> dict[str, dict]:
    """YAML mapping for ``editorial-board.yml`` (active editors)."""
    out: dict[str, dict] = {}
    for username in sorted(roster):
        entry = roster[username]
        if not entry.is_active:
            continue
        out[username] = {
            "peer_review_lead": entry.active_peer_review_lead,
            "eic": entry.active_eic,
            "triage": entry.active_triage,
            "emeritus_peer_review_lead": entry.emeritus_peer_review_lead,
            "emeritus_eic": entry.emeritus_eic,
            "emeritus_triage": entry.emeritus_triage,
        }
    return out


def emeritus_yaml(roster: dict[str, RosterEntry]) -> dict[str, dict]:
    """YAML mapping for ``emeritus-editors.yml``."""
    out: dict[str, dict] = {}
    for username in sorted(roster):
        entry = roster[username]
        if entry.is_active:
            continue
        out[username] = {
            "emeritus_editor": True,
            "emeritus_peer_review_lead": entry.emeritus_peer_review_lead,
            "emeritus_eic": entry.emeritus_eic,
            "emeritus_triage": entry.emeritus_triage,
        }
    return out


def editorial_titles(entry: RosterEntry) -> list[str]:
    """Titles that match the peer-review page role flags."""
    titles: list[str] = []
    if entry.is_active:
        # Base Editor always; specialties are additive.
        titles.append("Editor")
        if entry.active_peer_review_lead:
            titles.append("Peer Review Lead")
        if entry.active_eic:
            titles.append("Editor in Chief")
        if entry.active_triage:
            titles.append("Peer Review Triage")
        if entry.emeritus_peer_review_lead:
            titles.append("Emeritus Peer Review Lead")
        if entry.emeritus_eic:
            titles.append("Emeritus Editor in Chief")
        if entry.emeritus_triage:
            titles.append("Emeritus Peer Review Triage")
        return titles

    if entry.emeritus_peer_review_lead:
        titles.append("Emeritus Peer Review Lead")
    if entry.emeritus_eic:
        titles.append("Emeritus Editor in Chief")
    if entry.emeritus_triage:
        titles.append("Emeritus Peer Review Triage")
    if not titles:
        titles.append("Emeritus Editor")
    return titles


def _as_title_list(title: Any) -> list[str]:
    if not title:
        return []
    if isinstance(title, str):
        return [title]
    return [item for item in title if item]


def _is_editorial_title(title: str) -> bool:
    return title in EDITORIAL_TITLE_STRINGS


def _dump_title(titles: list[str]) -> str | list[str] | None:
    if not titles:
        return None
    if len(titles) == 1:
        return titles[0]
    return titles


def sync_titles(
    existing_title: Any, editorial: list[str] | None
) -> str | list[str] | None:
    """Replace editorial title strings; keep any other titles."""
    kept = [
        title
        for title in _as_title_list(existing_title)
        if not _is_editorial_title(title)
    ]
    combined: list[str] = []
    seen: set[str] = set()
    for title in list(editorial or []) + kept:
        if title not in seen:
            seen.add(title)
            combined.append(title)
    return _dump_title(combined)


def _ensure_list(value: Any) -> list:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def apply_roster_to_contributors(
    contribs: list[dict],
    roster: dict[str, RosterEntry],
    fetch_user: Callable[[str], dict] | None = None,
) -> None:
    """Set editorial flags and titles on contributor rows in place.

    Mutates ``contribs`` directly: existing row order is preserved and new
    team members are appended. Returns ``None``.
    """
    by_user: dict[str, dict] = {}
    for person in contribs:
        username = (person.get("github_username") or "").strip().lower()
        if username:
            by_user[username] = person

    for username, person in by_user.items():
        if username in roster:
            entry = roster[username]
            person["editorial_board"] = entry.is_active
            person["emeritus_editor"] = not entry.is_active
            person["title"] = sync_titles(
                person.get("title"), editorial_titles(entry)
            )
            if entry.is_active:
                contrib_types = _ensure_list(person.get("contributor_type"))
                if "editor" not in [item.lower() for item in contrib_types]:
                    contrib_types.append("editor")
                    person["contributor_type"] = contrib_types
            continue

        # Never remove emeritus status. Some emeritus editors are not in a
        # GitHub team (e.g. people who never joined the org), so they won't
        # be in the roster. Preserve their flag and title as-is.
        if person.get("emeritus_editor"):
            person["editorial_board"] = False
            continue

        person["editorial_board"] = False
        person["emeritus_editor"] = False
        person["title"] = sync_titles(person.get("title"), None)

    for username, entry in roster.items():
        if username in by_user:
            continue
        info = (fetch_user(username) if fetch_user else None) or {}
        stub = {
            "github_username": info.get("github_username") or username,
            "github_image_id": info.get("github_image_id"),
            "name": info.get("name"),
            "title": _dump_title(editorial_titles(entry)),
            "editorial_board": entry.is_active,
            "emeritus_editor": not entry.is_active,
            "contributor_type": ["editor"] if entry.is_active else [],
        }
        contribs.append(stub)
