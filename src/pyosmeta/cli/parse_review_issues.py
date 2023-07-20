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

# TODO: PRIORITIZE currently this recreates the review from scratch. but sometimes we might
# update content manually.
# TODO: add the link to the review issue to each package listing so we can link
# to the review from the website.
# TODO: if we export files we might want packages.yml and then under_review.yml
# thus we'd want to add a second input parameters which was file_name
# TODO: Would be cool to create an "under review now" list as well -
# ideally this could be passed as a CLI argument with the label we want to
# search for
# TODO: ASFSGAP has this  Data visualization - see presubmission so that becomes the category.
# a fix for this would be to check / validate  each category maybe at the end
# ?

import pickle

from pyosmeta import ProcessIssues
from pyosmeta.file_io import get_api_token


def main():
    GITHUB_TOKEN = get_api_token()

    issueProcess = ProcessIssues(
        org="pyopensci",
        repo_name="software-submission",
        label_name="6/pyOS-approved 🚀🚀🚀",
        GITHUB_TOKEN=GITHUB_TOKEN,
    )

    # Get all issues for approved packages
    issues = issueProcess.return_response()
    review = issueProcess.parse_issue_header(issues, 12)

    repo_endpoints = issueProcess.get_repo_endpoints(review)

    # Send a GET request to the API endpoint and include user agent header
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
        review[package_name]["gh_meta"] = all_repo_meta[package_name]

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(review, f)

    # Export and clean final yaml file
    issueProcess.clean_export_yml(review, "packages.yml")


if __name__ == "__main__":
    main()
