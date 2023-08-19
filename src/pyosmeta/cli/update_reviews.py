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

from pydantic import ValidationError

from pyosmeta import ProcessIssues, ReviewModel
from pyosmeta.file_io import load_website_yml

# todo - dates are wrong in issues

#   date_accepted: 5-2023-7
#   created_at: 01-2023-03
#   updated_at: 27-2023-07


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
        update_all = False
    web_reviews_path = (
        "https://raw.githubusercontent.com/pyOpenSci/"
        "pyopensci.github.io/main/_data/packages.yml"
    )

    process_review = ProcessIssues(
        org="pyopensci",
        repo_name="software-submission",
        label_name="6/pyOS-approved 🚀🚀🚀",
    )

    # Open web yaml & return dict with package name as key
    web_reviews = load_website_yml(key="package_name", url=web_reviews_path)

    # Get all issues for approved packages
    issues = process_review.return_response()
    accepted_reviews = process_review.parse_issue_header(issues, 15)

    # Parse through reviews, identify new ones, fix case
    if update_all:
        for key, meta in accepted_reviews.items():
            web_reviews[key.lower()] = meta
    else:
        for key, meta in accepted_reviews.items():
            if key.lower() not in web_reviews.keys():
                print("Yay - pyOS has a new package:", key)
                web_reviews[key.lower()] = meta

    # Update gh metrics via api for all packages
    # TODO: for some reason cardsort is missing gh_metadata
    repo_endpoints = process_review.get_repo_endpoints(web_reviews)
    web_reviews = process_review.get_gh_metrics(repo_endpoints, web_reviews)

    # Finally populate model objects with review data + metrics
    # TODO: this is really close - it's erroring when populating date
    # i suspect in the github metadata
    all_reviews = {}
    for key, review in web_reviews.items():
        # First add gh meta to each dict
        print("Parsing & validating", key)
        try:
            all_reviews[key] = ReviewModel(**review)
        except ValidationError as ve:
            print(key, ":", ve)

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(all_reviews, f)


if __name__ == "__main__":
    main()
