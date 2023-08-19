"""
This script parses through our reviews and contributors and:

1. Updates reviewer, editor and maintainer data in the contributor.yml file to
ensure all packages they supported are listed there.
1b: And that they have a listing as peer-review under contributor type
2. Updates the packages metadata with the participants names if it's missing
3. FUTURE: finally it looks to see if we are missing review participants from
the review issues in the contributor file and updates that file.

This script assumes that update_contributors and update_reviews has been run.
Rather than hit any api's it just updates information from the issues.
To run: update_reviewers

# TODO - FEATURE we have some packages that were NOT approved but we had
# editors and reviewers.
# We need to acknowledge these people as well. maybe tag them with waiting on
# maintainer response??
# TODO: package-wide feature: create no update flag for entries
# TODO: make sure we can add a 3rd or 4th reviewer - crowsetta has this as
# will biocypher
# TODO: make sure to add a current editor boolean to the current editors and
# emeritus ones.

"""

# TODO - Case sensitivity is an issue with my validation using set
#     - jointly
# - Jointly
# - devicely
# - Devicely
# - sevivi
import os

from pyosmeta.contributors import PersonModel, ProcessContributors
from pyosmeta.file_io import clean_export_yml, load_pickle


def get_clean_user(username: str) -> str:
    """A small helper that removes whitespace and ensures username is
    lower case"""
    return username.lower().strip()


def main():
    # TODO: move refresh contribs and contribs dict attr to
    # processContribs and remove this module altogether
    process_contribs = ProcessContributors([])

    # Two pickle files are outputs of the two other scripts
    # use that data to limit web calls
    contribs = load_pickle("all_contribs.pickle")
    packages = load_pickle("all_reviews.pickle")

    contrib_types = process_contribs.contrib_types

    for pkg_name, issue_meta in packages.items():
        print("Processing review team for:", pkg_name)
        for issue_role in contrib_types.keys():
            # I wonder if there is a clever way to skip review if this is missing?
            if issue_role == "all_current_maintainers":
                # if issue_meta.all_current_maintainers:
                # Loop through each maintainer in the list
                for i, a_maintainer in enumerate(
                    issue_meta.all_current_maintainers
                ):
                    gh_user = get_clean_user(a_maintainer["github_username"])

                    if gh_user not in contribs.keys():
                        contribs.update(
                            process_contribs.check_add_user(gh_user, contribs)
                        )

                    # Update user package contributions (if it's unique)
                    review_key = contrib_types[issue_role][0]
                    contribs[gh_user].add_unique_value(review_key, pkg_name)

                    # Update user contrib list (if it's unique)
                    review_roles = contrib_types[issue_role][1]
                    contribs[gh_user].add_unique_value(
                        "contributor_type", review_roles
                    )

                    # If name is missing in issue, populate from contribs
                    if a_maintainer["name"] == "":
                        name = getattr(contribs[gh_user], "name")
                        packages[pkg_name].all_current_maintainers[i][
                            "name"
                        ] = name

            else:
                # Else we are processing editors, reviewers...
                gh_user = get_clean_user(
                    getattr(packages[pkg_name], issue_role)["github_username"]
                )

                if gh_user not in contribs.keys():
                    # If they aren't already in contribs, add them
                    print("Found a new user!", gh_user)
                    new_contrib = process_contribs.get_user_info(gh_user)
                    contribs[gh_user] = PersonModel(**new_contrib)

                # Update user package contributions (if it's unique)
                review_key = contrib_types[issue_role][0]
                contribs[gh_user].add_unique_value(review_key, pkg_name)

                # Update user contrib list (if it's unique)
                review_roles = contrib_types[issue_role][1]
                contribs[gh_user].add_unique_value(
                    "contributor_type", review_roles
                )

                # If users's name is missing in issue, populate from contribs
                if getattr(issue_meta, issue_role)["name"] == "":
                    attribute_value = getattr(packages[pkg_name], issue_role)
                    attribute_value["name"] = getattr(
                        contribs[gh_user], "name"
                    )

    print("Export")
    # Export to yaml
    contribs_ls = [model.model_dump() for model in contribs.values()]
    # Getting error dumping packages
    pkgs_ls = [model.model_dump() for model in packages.values()]

    clean_export_yml(contribs_ls, os.path.join("_data", "contributors.yml"))
    clean_export_yml(pkgs_ls, os.path.join("_data", "packages.yml"))


if __name__ == "__main__":
    main()
