"""
Script that parses metadata from and issue and adds it to a .yml file for the
website. It also grabs some of the package metadata such as stars,
last commit, etc.

This script also checks:
* That each packages documentation is both https compliant and resolves
* If documentation link is broken it removes it.
* NOTE: we may want to have the website note if docs are not available for a
package and have a process to followup

Output: packages.yml file containing a list of:
 1. all packages with accepted reviews
 2. information related to the review including reviewers, editors
 3. basic package stats including stars, etc.
 4. partner information

To run at the CLI: parse_issue_metadata
"""

# TODO: if we export files we might want packages.yml and then under_review.yml
# thus we'd want to add a second input parameters which was file_name
# TODO: feature - Create an "under review now" list as well

import pickle

from pyosmeta import ProcessIssues
from pyosmeta.github_api import GitHubAPI
from pyosmeta.logging import logger


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
    all_reviews = github_api.get_gh_metrics(repo_paths, accepted_reviews)

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(all_reviews, f)


if __name__ == "__main__":
    main()
