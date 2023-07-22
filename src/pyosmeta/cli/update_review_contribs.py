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
"""
# TODO - FEATURE we have some packages that were NOT approved but we had editors and reviewers.
# We need to acknowledge these people as well. maybe tag them with waiting on maintainer response??
# TODO: package-wide feature: create a flag for entries that we do not want to update
# TODO: make sure we can add a 3rd or 4th reviewer - crowsetta has this as
# will biocypher
# TODO: make sure to add a current editor boolean to the current editors and
# emeritus ones.
# TODO - ?create a class for person types??


import pickle
from typing import Dict, List, Optional, Tuple, Union

from pyosmeta.contrib_review_meta import UpdateReviewMeta
from pyosmeta.file_io import get_api_token


def get_clean_user(username: str):
    return username.lower().strip()


def main():
    GITHUB_TOKEN = get_api_token()
    updateContribs = UpdateReviewMeta(GITHUB_TOKEN)

    # Two pickle files are outputs of the two other scripts
    # use that data to avoid having to hit the API again to retrieve.
    with open("all_contribs.pickle", "rb") as f:
        contribs = pickle.load(f)

    # Open packages yaml created by running parse_review_issues.py
    with open("all_reviews.pickle", "rb") as f:
        packages = pickle.load(f)

    contrib_types = updateContribs.contrib_types

    for pkg_name, issue_meta in packages.items():
        print("Processing review team for:", pkg_name)
        for issue_role in contrib_types.keys():
            if issue_role == "all_current_maintainers":
                if issue_role in issue_meta:
                    # Loop through each maintainer in the list
                    for i, a_maintainer in enumerate(issue_meta.get(issue_role)):
                        gh_user = get_clean_user(a_maintainer["github_username"])

                        if gh_user not in contribs.keys():
                            contribs.update(
                                updateContribs.check_add_user(gh_user, contribs)
                            )

                        # Update contrib packages for peer review
                        (
                            contrib_key,
                            pkg_list,
                        ) = updateContribs.refresh_contribs(
                            contribs[gh_user],
                            pkg_name,  # new contribs
                            issue_role,
                        )
                        # Update users contrib list
                        contribs[gh_user][contrib_key] = pkg_list

                        _, contrib_list = updateContribs.refresh_contribs(
                            contribs[gh_user],
                            None,
                            issue_role,
                        )
                        contribs[gh_user]["contributor_type"] = contrib_list

                        # If name is missing in issue summary, populate from contribs
                        if a_maintainer["name"] == "":
                            packages[pkg_name]["all_current_maintainers"][i][
                                "name"
                            ] = contribs[gh_user]["name"]

                else:
                    print(
                        "All maintainers is missing in the review for ",
                        pkg_name,
                    )

            else:
                # Else we are processing editors, reviewers...
                gh_user = get_clean_user(
                    packages[pkg_name][issue_role]["github_username"]
                )

                if gh_user not in contribs.keys():
                    # If they aren't already in contribs, add them
                    contribs.update(updateContribs.check_add_user(gh_user, contribs))
                # Update user package contributions
                (
                    contrib_key,
                    pkg_list,
                ) = updateContribs.refresh_contribs(
                    contribs[gh_user],
                    pkg_name,  # new contribs
                    issue_role,
                )

                # Update users contrib list
                contribs[gh_user][contrib_key] = pkg_list

                _, contrib_list = updateContribs.refresh_contribs(
                    contribs[gh_user],
                    None,
                    issue_role,
                )
                contribs[gh_user]["contributor_type"] = contrib_list

                # If users's name is missing in issue, populate from contribs dict
                if issue_meta[issue_role]["name"] == "":
                    packages[pkg_name][issue_role]["name"] = contribs[gh_user]["name"]

    # Export to yaml
    updateContribs.clean_export_yml(contribs, "contribs.yml")
    updateContribs.clean_export_yml(packages, "packs.yml")


if __name__ == "__main__":
    main()
