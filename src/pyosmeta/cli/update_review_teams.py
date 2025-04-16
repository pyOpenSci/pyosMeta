"""
This script parses through our packages.yml and contributors.yml files
and:

1. Updates reviewer, editor and maintainer data in the contributor.yml file to
ensure all packages they supported are listed there.
1b: And that they have a listing as peer-review under contributor type
3. Finally it looks to see if we are missing review participants from
the review issues in the contributor file and updates that file.

This script assumes that update_contributors and update_reviews has been run.
Rather than hit any api's it just updates information from the issues.
To run: update_reviewers

# TODO - FEATURE we have some packages that were NOT approved but we had
# editors and reviewers who participated. We need to acknowledge these people
# Make sure each issue is tagged "on hold" and then parse contributions
# TODO: make sure the script recognizes a 3rd or 4th reviewer - crowsetta has
# this as will biocypher

"""

import os
from datetime import datetime

from pydantic import ValidationError
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import clean_export_yml, load_pickle
from pyosmeta.github_api import GitHubAPI
from pyosmeta.logging import logger
from pyosmeta.models import PersonModel, ReviewModel, ReviewUser
from pyosmeta.utils_clean import get_clean_user


def process_user(
    user: ReviewUser,
    role: str,
    pkg_name: str,
    contribs: dict[str, PersonModel],
    processor: ProcessContributors,
) -> tuple[ReviewUser, dict[str, PersonModel]]:
    """Updates a ReviewUser which represents software review participant

    The contributor entry looks something like this:
    https://github.com/pyOpenSci/pyopensci.github.io/blob/main/_data/contributors.yml
    - name: First Last
        github_username: ghid
        github_image_id: 7649194
        contributor_type:
        - editor
        - package-guide
        - package-maintainer
        - peer-review
        - submitting-author
    packages_editor:
        - errdapy
        - nbless
        - pandera
        - pygmt
        - pyrolite
    packages_submitted:
        - earthpy
    packages_reviewed:

    This function updates contributor's contribution types entries and the
     package reviews that they's contributed to in the `contribs` object which
    gets dumped into our contributors.yml file in the website repo.

    It also updates the contributors human name (if only the GitHub username is
    available in packages.yml) in
     the packages object IF that name is available in the contributors.yml file.

     Finally, if the contributor is new and not yet in our contributors.yml file,
     it adds them to the contribs object

    Parameters
    ----------
    user : ReviewUser
        The user object representing a person involved in the peer review process.
        Must have a GitHub username to process their data. Name is optional and
        is looked up from the contribs dict
    role : str
        The role of the user in the review process (e.g., "reviewer", "editor").
        Used to update their contributions in the contribs dict
    pkg_name : str
        The name of the package the user is contributing to or reviewing.
        Used to update their list of packages that they've supported through
        the review process
    contribs : dict[str, PersonModel]
        A dictionary mapping GitHub usernames to `PersonModel` objects. This
        contains information about all contributors and is updated in
        this function.
    processor : ProcessContributors
        A utility object for handling contributor processing logic, including
        role mapping and fetching contributor details.

    Returns
    -------
    tuple[ReviewUser, dict[str, PersonModel]]
        - Updated `user` object, potentially with additional details (e.g., name).
        - Updated `contribs` dictionary, including any new contributor or or
        updated data for existing contributors.
    """
    gh_user = get_clean_user(user.github_username)

    if gh_user not in contribs.keys():
        # If they aren't in the existing contribs.yml data, add them by using
        # their github username and hitting the github api
        logger.info(f"Found a new contributor: {gh_user}")
        new_contrib = processor.return_user_info(gh_user)
        new_contrib["date_added"] = datetime.now().strftime("%Y-%m-%d")
        try:
            contribs[gh_user] = PersonModel(**new_contrib)
        except ValidationError:
            logger.error(
                f"Error processing new contributor {gh_user}. Skipping this user.",
                exc_info=True,
            )

    # Update user the list of contribution types if there are new types to add
    # for instance a new reviewer would have a "Reviewer" contributor type
    # added to their contributors.yml entry. But if reviewer is already in the
    # list we don't need to have it twice!
    review_key = processor.contrib_types[role][0]
    contribs[gh_user].add_unique_value(review_key, pkg_name.lower())

    # Update users contribution type list (if the role is not already there)
    review_roles = processor.contrib_types[role][1]
    contribs[gh_user].add_unique_value("contributor_type", review_roles)

    # If users's name is missing in issue, populate from contribs dict.
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

    for pkg_name, review in tqdm(
        packages.items(), desc="Processing review teams"
    ):
        with logging_redirect_tqdm():
            tqdm.write(f"Processing review team for: {pkg_name}")
            for role in contrib_types.keys():
                user: list[ReviewUser] | ReviewUser = getattr(review, role)

                # Eic is a newer field, so in some instances it will be empty
                # if it's empty log a message noting the data are missing
                if user:
                    # Handle lists or single users separately
                    if isinstance(user, list):
                        for i, a_user in enumerate(user):
                            a_user, contribs = process_user(
                                a_user,
                                role,
                                pkg_name,
                                contribs,
                                process_contribs,
                            )
                            # Update individual user in reference to issue list
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
                else:
                    logger.warning(
                        f"I can't find a username for {role} under {pkg_name}. Moving on."
                    )

    # Export to yaml
    contribs_ls = [model.model_dump() for model in contribs.values()]
    pkgs_ls = [model.model_dump() for model in packages.values()]

    clean_export_yml(contribs_ls, os.path.join("_data", "contributors.yml"))
    clean_export_yml(pkgs_ls, os.path.join("_data", "packages.yml"))


if __name__ == "__main__":
    main()
