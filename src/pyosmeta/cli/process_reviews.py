"""
Script that parses metadata from an issue and adds it to a .yml file for the
website. It also grabs some of the package metadata such as stars,
last commit, etc.

This script also checks:
* That each package's documentation is both https compliant and resolves
* If documentation link is broken it removes it.
* NOTE: we may want to have the website note if docs are not available for a
package and have a process to follow-up

Output: packages.yml file containing a list of:
 1. all packages with accepted reviews
 2. information related to the review including reviewers, editors
 3. basic package stats including stars, etc.
 4. partner information

To run at the CLI: parse_issue_metadata
"""

# TODO: if we export files we might want packages.yml and then under_review.yml
# thus we'd want to add a second input parameter which was file_name
# TODO: feature - Create an "under review now" list as well

import pickle

from pydantic import ValidationError

from pyosmeta import ProcessIssues
from pyosmeta.constants import PACKAGES_RAW_URL
from pyosmeta.file_io import load_website_yml
from pyosmeta.github_api import GitHubAPI
from pyosmeta.logging import logger
from pyosmeta.models import ReviewModel
from pyosmeta.models.base import GhMeta


def get_existing_gh_meta(url: str = PACKAGES_RAW_URL) -> dict[str, GhMeta]:
    """Load the currently published packages.yml and pull out the
    ``gh_meta`` block for each package, keyed by lowercased package name.

    Used by ``update_gh_meta`` as a backup when a fresh GitHub API fetch
    leaves ``gh_meta`` empty. Does not itself apply metrics to reviews.

    Parameters
    ----------
    url : str
        URL to the live packages.yml file.

    Returns
    -------
    dict
        Mapping of lowercased package name to its last known ``GhMeta``.
        Packages with no previously saved (or no longer valid) metrics are
        omitted.
    """
    # TODO: fail fast if packages.yml cannot be loaded (separate follow-up).
    try:
        existing_packages = load_website_yml("package_name", url)
    except Exception:
        logger.error(
            "Couldn't load the existing packages.yml. Continuing without "
            "a fallback for any GitHub metrics fetches that fail this run.",
            exc_info=True,
        )
        return {}

    existing_gh_meta = {}
    for name, pkg in existing_packages.items():
        if not pkg.get("gh_meta"):
            continue
        try:
            existing_gh_meta[name] = GhMeta(**pkg["gh_meta"])
        except ValidationError:
            logger.error(
                f"Existing gh_meta for {name} in the live packages.yml "
                "doesn't match the current GhMeta model. Skipping it as a "
                "fallback.",
                exc_info=True,
            )

    return existing_gh_meta


def update_gh_meta(
    existing_gh_meta: dict[str, GhMeta],
    reviews: dict[str, ReviewModel],
) -> dict[str, ReviewModel]:
    """Fill in missing gh_meta from previously published packages.yml.

    Fresh API data (already on ``review.gh_meta``) wins. If a fetch left
    ``gh_meta`` as None, reuse the last known ``GhMeta`` for that package.
    """
    for pkg_name, review in reviews.items():
        if review.gh_meta is not None:
            continue

        previous_metadata = existing_gh_meta.get(pkg_name.lower())
        if previous_metadata is not None:
            logger.warning(
                f"Couldn't refresh GitHub metrics for {pkg_name}. "
                "Using the previously saved metrics from packages.yml."
            )
            review.gh_meta = previous_metadata
        else:
            logger.warning(
                f"No GitHub metrics available for {pkg_name} "
                "(none saved previously, and this fetch failed)."
            )

    return reviews


def main():
    github_api = GitHubAPI(
        org="pyopensci",
        repo="software-submission",
        labels=["6/pyOS-approved"],
    )

    process_review = ProcessIssues(github_api)

    # Get all issues for approved packages - load as dict
    issues = process_review.get_issues()
    accepted_reviews, errors = process_review.parse_issues(issues)
    if errors:
        logger.error("Errors found when parsing reviews (printed to stdout):")
        for url, error in errors.items():
            print(f"Error in review at url: {url}")
            print(error)
            print("-" * 20)
        raise RuntimeError("Errors in parsing reviews, see printout above")

    # Update gh metrics via api for all packages
    # Contrib count is only available via rest api
    logger.info("Getting GitHub metrics for all packages...")
    repo_paths = process_review.get_repo_paths(accepted_reviews)
    # Fetch first; gap-fill from packages.yml only where the API left gh_meta empty
    existing_gh_meta = get_existing_gh_meta()
    all_reviews = github_api.get_metrics(repo_paths, accepted_reviews)
    all_reviews = update_gh_meta(existing_gh_meta, all_reviews)

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(all_reviews, f)


if __name__ == "__main__":
    main()
