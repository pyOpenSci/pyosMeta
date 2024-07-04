"""
Script that parses metadata from and issue and adds it to a .yml file for the
website. It also grabs some of the package metadata such as stars,
last commit, etc.

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


def main():
    github_api = GitHubAPI(
        org="pyopensci",
        repo="software-submission",
        labels=["6/pyOS-approved"],
    )

    process_review = ProcessIssues(github_api)

    # Get all issues for approved packages - load as dict
    # TODO: this doesn't have to be in process issues at all. it could fully
    # Call the github module
    issues = process_review.get_issues()
    accepted_reviews, errors = process_review.parse_issues(issues)
    for url, error in errors.items():
        print(f"Error in review at url: {url}")
        print(error)
        print("-" * 20)

    # Update gh metrics via api for all packages
    repo_endpoints = process_review.get_repo_endpoints(accepted_reviews)
    all_reviews = process_review.get_gh_metrics(
        repo_endpoints, accepted_reviews
    )

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(all_reviews, f)


if __name__ == "__main__":
    main()
