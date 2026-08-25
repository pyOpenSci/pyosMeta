"""Single source of truth for pyOpenSci website data paths and editor teams.

These constants are used across the CLI scripts to read and write
`contributors.yml` and `packages.yml`, which live in the `data/` directory of
the pyopensci.github.io (Hugo) website repo, and to name the GitHub org
teams that are the source of truth for editor listings. Update the values
here rather than hardcoding them in individual scripts.
"""

# Reused by file_io.create_paths() to build .all-contributorsrc URLs for
# other pyOpenSci repos, so it must stay org-level (no repo name baked in).
RAW_BASE_URL = "https://raw.githubusercontent.com/pyOpenSci/"

# Shared prefix for website data files on GitHub (always POSIX `/`).
WEBSITE_DATA_DIR = "data"
WEBSITE_DATA_RAW_URL = (
    f"{RAW_BASE_URL}pyopensci.github.io/refs/heads/main/{WEBSITE_DATA_DIR}/"
)

CONTRIBUTORS_FILE = "contributors.yml"
PACKAGES_FILE = "packages.yml"
EDITORIAL_BOARD_FILE = "editorial-board.yml"
EMERITUS_EDITORS_FILE = "emeritus-editors.yml"

# POSIX repo-relative locations of the data files *inside* the website repo.
# Use these for git operations (e.g. `repo.git.show("<sha>:<path>")`) and to
# reference where a file lives in the repo -- NOT as a local filesystem write
# target. To write files, take a `--data-dir` at runtime and build the path
# with `file_io.get_output_path(data_dir, <FILE constant>)`.
CONTRIBUTORS_REL_PATH = f"{WEBSITE_DATA_DIR}/{CONTRIBUTORS_FILE}"
PACKAGES_REL_PATH = f"{WEBSITE_DATA_DIR}/{PACKAGES_FILE}"

CONTRIBUTORS_RAW_URL = f"{WEBSITE_DATA_RAW_URL}{CONTRIBUTORS_FILE}"
PACKAGES_RAW_URL = f"{WEBSITE_DATA_RAW_URL}{PACKAGES_FILE}"
EDITORIAL_BOARD_RAW_URL = f"{WEBSITE_DATA_RAW_URL}{EDITORIAL_BOARD_FILE}"
EMERITUS_EDITORS_RAW_URL = f"{WEBSITE_DATA_RAW_URL}{EMERITUS_EDITORS_FILE}"

# Single source of truth for pyOpenSci repos whose all-contributors bot data
# feeds into contributors.yml, and the contribution-type category each repo's
# contributors should be tagged with. update_contributors.py uses the keys to
# build .all-contributorsrc URLs (via file_io.create_paths()); contributors.py
# uses the mapping in check_contrib_type() to classify each repo's
# contributors. Add a repo here to included it in the list of repositories that
# we acknowledge contributors for helping with.
REPO_CONTRIB_TYPES: dict[str, str] = {
    "software-submission": "peer-review-guide",
    "software-peer-review": "peer-review-guide",
    "python-package-guide": "package-guide",
    "pyosPackage": "package-guide",
    "pyos-package-template": "package-guide",
    "lessons": "open-education",
    "pyopensci.github.io": "web-contrib",
    "pyosMeta": "code-contrib",
    "metrics": "code-contrib",
    "software-review": "community",
    "handbook": "community",
    "pyos-sphinx-theme": "community",
}

CONTRIB_REPOS = list(REPO_CONTRIB_TYPES.keys())

# GitHub org team slugs used as the source of truth for editor listings.
# Membership is managed on GitHub; pyosMeta reads these teams.
EDITORIAL_TEAMS: dict[str, str] = {
    "editorial_board": "editorial-board",
    "emeritus_editors": "emeritus-editors",
    "eic_team": "eic-team",
    "peer_review_lead": "peer-review-lead",
}
