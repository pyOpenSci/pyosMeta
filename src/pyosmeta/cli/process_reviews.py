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

from pydantic import ValidationError

from pyosmeta import ProcessIssues, ReviewModel


def main():
    process_review = ProcessIssues(
        org="pyopensci",
        repo_name="software-submission",
        label_name="6/pyOS-approved 🚀🚀🚀",
    )

    # Get all issues for approved packages - load as dict
    issues = process_review.return_response()
    # TODO: this method parse_issue_header is working but the parsing code is
    # hard to follow
    accepted_reviews = process_review.parse_issue_header(issues, 45)

    # Update gh metrics via api for all packages
    repo_endpoints = process_review.get_repo_endpoints(accepted_reviews)
    all_reviews = process_review.get_gh_metrics(
        repo_endpoints, accepted_reviews
    )

    # Populate model objects with review data + metrics
    final_reviews = {}
    for key, review in all_reviews.items():
        # First add gh meta to each dict
        print("Parsing & validating", key)
        try:
            final_reviews[key] = ReviewModel(**review)
        except ValidationError as ve:
            print(key, ":", ve)

    with open("all_reviews.pickle", "wb") as f:
        pickle.dump(final_reviews, f)


if __name__ == "__main__":
    main()
