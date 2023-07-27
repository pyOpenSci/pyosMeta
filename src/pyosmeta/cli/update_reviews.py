"""
Script that parses metadata from na issue and adds it to a yml file for the
website. It also grabs some of the package metadata such as stars,
last commit, etc.

Output: packages.yml file containing a list of
 1. all packages with accepted reviews
 2. information related to the review including reviewers, editors
 3. basic package stats including stars, etc.

To run at the CLI: parse_issue_metadata
"""

# TODO: if we export files we might want packages.yml and then under_review.yml
# thus we'd want to add a second input parameters which was file_name
# TODO: feature - Would be cool to create an "under review now" list as well -
# ideally this could be passed as a CLI argument with the label we want to
# search for

import argparse
import pickle

from pyosmeta import ProcessIssues
from pyosmeta.file_io import clean_export_yml, load_website_yml


def main():
    update_all = False
    parser = argparse.ArgumentParser(
        description="A CLI script to update pyOpenSci reviews"
    )
    parser.add_argument(
        "--update",
        type=str,
        help="Will force update review info from GitHub for every review",
    )
    args = parser.parse_args()

    if args:
        update_all = True

    web_reviews_path = "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/_data/packages.yml"

    issueProcess = ProcessIssues(
        org="pyopensci",
        repo_name="software-submission",
        label_name="6/pyOS-approved 🚀🚀🚀",
    )

    # Open web yaml & return dict with package name as key
    web_reviews = load_website_yml(key="package_name", url=web_reviews_path)

    # Get all issues for approved packages
    issues = issueProcess.return_response()
    all_accepted_reviews = issueProcess.parse_issue_header(issues, 15)

    # Parse through reviews, identify new ones, fix case
    if update_all == True:
        for review_key, review_meta in all_accepted_reviews.items():
            web_reviews[review_key.lower()] = review_meta
    else:
        for review_key, review_meta in all_accepted_reviews.items():
            if review_key.lower() not in web_reviews.keys():
                print("Yay - pyOS has a new package:", review_key)
                web_reviews[review_key.lower()] = review_meta

    # Update gh metrics via api for all packages
    repo_endpoints = issueProcess.get_repo_endpoints(web_reviews)
    gh_stats = [
        "name",
        "description",
        "homepage",
        "created_at",
        "stargazers_count",
        "watchers_count",
        "forks",
        "open_issues_count",
        "forks_count",
    ]

    # Get gh metadata for each package submission
    all_repo_meta = {}
    for package_name in repo_endpoints.keys():
        print("Getting GitHub stats for", package_name)
        package_api = repo_endpoints[package_name]
        all_repo_meta[package_name] = issueProcess.get_repo_meta(package_api, gh_stats)

        all_repo_meta[package_name]["contrib_count"] = issueProcess.get_repo_contribs(
            package_api
        )
        all_repo_meta[package_name]["last_commit"] = issueProcess.get_last_commit(
            package_api
        )
        # Add github meta to review metadata
        web_reviews[package_name]["gh_meta"] = all_repo_meta[package_name]

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(web_reviews, f)


if __name__ == "__main__":
    main()
