"""Single source of truth for paths and URLs to pyOpenSci website data files.

These constants are used across the CLI scripts to read and write
`contributors.yml` and `packages.yml`, which live in the `data/` directory of
the pyopensci.github.io (Hugo) website repo. Update the values here rather
than hardcoding them in individual scripts.
"""

# Reused by file_io.create_paths() to build .all-contributorsrc URLs for
# other pyOpenSci repos, so it must stay org-level (no repo name baked in).
RAW_BASE_URL = "https://raw.githubusercontent.com/pyOpenSci/"

# Shared prefix for both website data files.
WEBSITE_DATA_RAW_URL = (
    f"{RAW_BASE_URL}pyopensci.github.io/refs/heads/main/data/"
)

CONTRIBUTORS_REL_PATH = "data/contributors.yml"
PACKAGES_REL_PATH = "data/packages.yml"

CONTRIBUTORS_RAW_URL = f"{WEBSITE_DATA_RAW_URL}contributors.yml"
PACKAGES_RAW_URL = f"{WEBSITE_DATA_RAW_URL}packages.yml"
