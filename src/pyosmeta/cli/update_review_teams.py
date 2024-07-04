"""
This script parses through our reviews and contributors and:

1. Updates reviewer, editor and maintainer data in the contributor.yml file to
ensure all packages they supported are listed there.
1b: And that they have a listing as peer-review under contributor type
2. Updates the packages metadata with the participants names if it's missing
3. Finally it looks to see if we are missing review participants from
the review issues in the contributor file and updates that file.

This script assumes that update_contributors and update_reviews has been run.
Rather than hit any api's it just updates information from the issues.
To run: update_reviewers

# TODO - FEATURE we have some packages that were NOT approved but we had
# editors and reviewers who participated. We need to acknowledge these people
# Make sure each issue is tagged "on hold" and then parse contributions
# TODO: package-wide feature: create no update flag for entries
# TODO: make sure the script recognizes a 3rd or 4th reviewer - crowsetta has
# this as will biocypher

"""

import os
from datetime import datetime

from pydantic import ValidationError
from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import clean_export_yml, load_pickle
from pyosmeta.github_api import GitHubAPI
from pyosmeta.models import PersonModel, ReviewModel, ReviewUser
from pyosmeta.utils_clean import get_clean_user


def process_user(
    user: ReviewUser,
    role: str,
    pkg_name: str,
    contribs: dict[str, PersonModel],
    processor: ProcessContributors,
) -> tuple[ReviewUser, dict[str, PersonModel]]:
    """
    - Add a new contributor to `contribs` (mutating it)
    - Add user to any reviews/etc. that they're on (i don't rly understand that part,
      someone else write these docs plz (mutating `contribs`)
    - get their human name from the github name, mutating the `user` object.
    """
    gh_user = get_clean_user(user.github_username)

    if gh_user not in contribs.keys():
        # If they aren't already in contribs, add them
        print("Found a new contributor!", gh_user)
        new_contrib = processor.return_user_info(gh_user)
        new_contrib["date_added"] = datetime.now().strftime("%Y-%m-%d")
        try:
            contribs[gh_user] = PersonModel(**new_contrib)
        except ValidationError as ve:
            print(ve)

    # Update user package contributions (if it's unique)
    review_key = processor.contrib_types[role][0]
    contribs[gh_user].add_unique_value(review_key, pkg_name.lower())

    # Update user contrib list (if it's unique)
    review_roles = processor.contrib_types[role][1]
    contribs[gh_user].add_unique_value("contributor_type", review_roles)

    # If users's name is missing in issue, populate from contribs
    if not user.name:
        user.name = getattr(contribs[gh_user], "name")

    return user, contribs


def main():
    github_api = GitHubAPI()
    process_contribs = ProcessContributors(github_api, [])

    # Two pickle files are outputs of the two other scripts
    # use that data to limit web calls
    contribs: dict[str, PersonModel] = load_pickle("all_contribs.pickle")
    packages: dict[str, ReviewModel] = load_pickle("all_reviews.pickle")

    contrib_types = process_contribs.contrib_types

    for pkg_name, review in packages.items():
        print("Processing review team for:", pkg_name)
        for role in contrib_types.keys():
            user: list[ReviewUser] | ReviewUser = getattr(review, role)

            # handle lists or singleton users separately
            if isinstance(user, list):
                for i, a_user in enumerate(user):
                    a_user, contribs = process_user(
                        a_user, role, pkg_name, contribs, process_contribs
                    )
                    # update individual user in reference to issue list
                    user[i] = a_user
            elif isinstance(user, ReviewUser):
                user, contribs = process_user(
                    user, role, pkg_name, contribs, process_contribs
                )
                setattr(review, role, user)
            else:
                raise TypeError(
                    "Keys in the `contrib_types` map must be a `ReviewUser` or `list[ReviewUser]` in the `ReviewModel`"
                )

    # Export to yaml
    contribs_ls = [model.model_dump() for model in contribs.values()]
    pkgs_ls = [model.model_dump() for model in packages.values()]

    clean_export_yml(contribs_ls, os.path.join("_data", "contributors.yml"))
    clean_export_yml(pkgs_ls, os.path.join("_data", "packages.yml"))


if __name__ == "__main__":
    main()
