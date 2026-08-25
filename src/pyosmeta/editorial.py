"""Build the editor roster from GitHub org team membership.

GitHub teams are the source of truth for who is active vs emeritus.
``emeritus_eic`` and ``emeritus_peer_review_lead`` are preserved from the
existing website YAML because those roles are historical, not a current team.
"""

from typing import Any, Callable

EDITORIAL_TITLE_STRINGS = frozenset(
    {
        "Editor",
        "Editor in Chief",
        "Editor in Chief Team",
        "Peer Review Lead",
        "Emeritus Editor",
        "Emeritus Editor in Chief",
        "Emeritus Peer Review Lead",
    }
)

TITLE_NORMALIZE = {
    "Editor in Chief Team": "Editor in Chief",
}


def _usernames(logins: list[str] | None) -> set[str]:
    return {
        (login or "").strip().lower()
        for login in (logins or [])
        if (login or "").strip()
    }


def _lower_keys(mapping: dict | None) -> dict:
    if not mapping:
        return {}
    return {str(key).strip().lower(): value for key, value in mapping.items()}


def build_roster(
    teams: dict[str, list[str]],
    previous: dict[str, dict] | None = None,
) -> dict[str, dict]:
    """Return username -> role flags from team membership.

    Parameters
    ----------
    teams : dict
        Mapping of ``EDITORIAL_TEAMS`` keys to GitHub logins.
    previous : dict, optional
        Combined existing ``editorial-board.yml`` and
        ``emeritus-editors.yml`` so historical emeritus role flags are
        kept.
    """
    previous = _lower_keys(previous)
    board = _usernames(teams.get("editorial_board"))
    emeritus = _usernames(teams.get("emeritus_editors"))
    eic = _usernames(teams.get("eic_team"))
    pr_lead = _usernames(teams.get("peer_review_lead"))

    active = board | eic | pr_lead
    emeritus_only = emeritus - active

    roster: dict[str, dict] = {}
    for username in active | emeritus_only:
        prev = previous.get(username) or {}
        if not isinstance(prev, dict):
            prev = {}
        is_active = username in active
        roster[username] = {
            "active": is_active,
            "peer_review_lead": username in pr_lead if is_active else False,
            "eic_team": username in eic if is_active else False,
            "emeritus_peer_review_lead": bool(
                prev.get("emeritus_peer_review_lead")
            ),
            "emeritus_eic": bool(prev.get("emeritus_eic")),
        }
    return roster


def board_yaml(roster: dict[str, dict]) -> dict[str, dict]:
    """YAML mapping for ``editorial-board.yml`` (active editors)."""
    out: dict[str, dict] = {}
    for username in sorted(roster):
        entry = roster[username]
        if not entry["active"]:
            continue
        out[username] = {
            "peer_review_lead": entry["peer_review_lead"],
            "eic_team": entry["eic_team"],
            "emeritus_peer_review_lead": entry["emeritus_peer_review_lead"],
            "emeritus_eic": entry["emeritus_eic"],
        }
    return out


def emeritus_yaml(roster: dict[str, dict]) -> dict[str, dict]:
    """YAML mapping for ``emeritus-editors.yml``."""
    out: dict[str, dict] = {}
    for username in sorted(roster):
        entry = roster[username]
        if entry["active"]:
            continue
        out[username] = {
            "emeritus_peer_review_lead": entry["emeritus_peer_review_lead"],
            "emeritus_eic": entry["emeritus_eic"],
        }
    return out


def editorial_titles(entry: dict) -> list[str]:
    """Titles that match the peer-review page role flags."""
    titles: list[str] = []
    if entry["active"]:
        if entry["peer_review_lead"]:
            titles.append("Peer Review Lead")
        if entry["eic_team"]:
            titles.append("Editor in Chief")
        if entry["emeritus_peer_review_lead"]:
            titles.append("Emeritus Peer Review Lead")
        if entry["emeritus_eic"]:
            titles.append("Emeritus Editor in Chief")
        if not titles:
            titles.append("Editor")
        return titles

    if entry["emeritus_peer_review_lead"]:
        titles.append("Emeritus Peer Review Lead")
    if entry["emeritus_eic"]:
        titles.append("Emeritus Editor in Chief")
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
    return (
        title in EDITORIAL_TITLE_STRINGS
        or TITLE_NORMALIZE.get(title) in EDITORIAL_TITLE_STRINGS
    )


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
    roster: dict[str, dict],
    fetch_user: Callable[[str], dict] | None = None,
) -> list[dict]:
    """Set editorial flags and titles on contributor rows.

    Existing row order is preserved. New team members are appended.
    """
    by_user: dict[str, dict] = {}
    for person in contribs:
        username = (person.get("github_username") or "").strip().lower()
        if username:
            by_user[username] = person

    for username, person in by_user.items():
        if username in roster:
            entry = roster[username]
            person["editorial_board"] = entry["active"]
            person["emeritus_editor"] = not entry["active"]
            person["title"] = sync_titles(
                person.get("title"), editorial_titles(entry)
            )
            if entry["active"]:
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
            "editorial_board": entry["active"],
            "emeritus_editor": not entry["active"],
            "contributor_type": ["editor"] if entry["active"] else [],
        }
        contribs.append(stub)

    return contribs
