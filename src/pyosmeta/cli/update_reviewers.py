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
# TODO: right now this just updates all packages. but in some cases, we may
# update the file itself (how often??) so it's worth considering a way to
# just update the current file and flag entries that we do not want to update
# TODO: add a key in the contributor_type list for submitting-author
# TODO: make sure we can add a 3rd or 4th reviewer - crowsetta has this as
# will biocypher
# TODO: make sure to add a current editor boolean to the current editors and
# emeritus ones.
# TODO: alex definitely contributed to the guides as well. I believe everyone is not being correctly assigned to guidebook contrib


import pickle
from typing import Dict, List, Optional, Tuple, Union

# from pyosmeta.contrib_review_meta import UpdateReviewMeta
from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import get_api_token

# import ruamel.yaml as yaml


# TODO: add these to a module
def check_add_user(gh_user: str, contribs: Dict[str, str], process_contribs) -> None:
    """"""
    if gh_user not in contribs.keys():
        print("Missing user", gh_user, "adding them now.")
        return contribs.update(process_contribs.add_new_user(gh_user))


def clean_list(a_list: Union[str, List[str]]) -> List[str]:
    """Helper function that takes an input object,
    removes 'None' if that is in the list. and returns
        either an empty clean list of the list as is."""

    if a_list == None or isinstance(a_list, str) or None in a_list:
        a_list = []

    return a_list


def unique_new_vals(
    a_list: List[str], a_item: List[str]
) -> Tuple[bool, Optional[List[str]]]:
    """Checks two objects either a list and string or two lists
    and evaluates whether there are differences between them."""

    default = (False, None)
    list_lower = [al.lower() for al in a_list]
    item_lower = [ai.lower() for ai in a_item]
    diff = list(set(item_lower) - set(list_lower))
    if len(diff) > 0:
        default = (True, diff)
    return default


def main():
    GITHUB_TOKEN = get_api_token()

    process_contribs = ProcessContributors([], [], GITHUB_TOKEN)
    # Open the contributor file created from parse_contributors.py
    # key is gh_username (lowercase)
    with open("all_contribs.pickle", "rb") as f:
        contribs = pickle.load(f)

    # Open packages yaml created by running parse_review_issues.py
    with open("all_reviews.pickle", "rb") as f:
        packages = pickle.load(f)

    ppl_types = {
        "reviewer_1": ["packages-reviewed", ["reviewer", "peer-review"]],
        "reviewer_2": ["packages-reviewed", ["reviewer", "peer-review"]],
        "editor": ["packages-editor", ["editor", "peer-review"]],
        "submitting_author": [
            "packages-submitted",
            ["maintainer", "submitting-author", "peer-review"],
        ],
        "all_current_maintainers": [
            "packages-submitted",
            ["maintainer", "peer-review"],
        ],
    }

    # TODO: ivan did an if/ else to treat roles with 1 entry person vs multiple
    # if maintainers, ..
    # TODO - ?create a class for person types??
    # Instead of using try/ except .get()

    for pkg_name, issue_meta in packages.items():
        print("Processing editors, author and reviewers:", pkg_name)

        for issue_review_role in ppl_types.keys():
            if issue_review_role == "all_current_maintainers":
                # Now parse all_current_maintainers
                print("Processing maintainers")
                # Might not use this but if so should be yml_role

                # Older issues don't have all_current maintainers key key
                if issue_review_role in issue_meta:
                    # Loop through each maintainer in the list
                    for i, a_maintainer in enumerate(issue_meta.get(issue_review_role)):
                        gh_user = a_maintainer["github_username"].lower().strip()
                        check_add_user(gh_user, contribs, process_contribs)
                        contrib_key_yml = ppl_types[issue_review_role][0]
                        contrib_pkgs = contribs[gh_user][contrib_key_yml]

                        # If name is missing in issue, populate from contribs
                        if a_maintainer["name"] == "":
                            packages[pkg_name]["all_current_maintainers"][i][
                                "name"
                            ] = contribs[gh_user]["name"]
                            # Add them to the correct maintainer key packages-submitted
                        # Update package list
                        contrib_pkg_list = clean_list(contrib_pkgs)
                        unique_vals, vals = unique_new_vals(
                            contrib_pkg_list, [pkg_name]
                        )
                        if unique_vals:
                            contrib_pkg_list += vals

                        # Update contrib role
                        contrib_types = contribs[gh_user]["contributor_type"]
                        review_roles = ppl_types[issue_review_role][1]
                        existing_contribs = clean_list(contrib_types)
                        unique_vals, vals = unique_new_vals(
                            existing_contribs, review_roles
                        )
                        if unique_vals:
                            existing_contribs += vals
                else:
                    print(
                        "All maintainers is missing in the review for ",
                        pkg_name,
                    )

            else:
                gh_user = (
                    packages[pkg_name][issue_review_role]["github_username"]
                    .lower()
                    .strip()
                )

                # If they aren't already in contribs, add them
                check_add_user(gh_user, contribs, process_contribs)
                contribs_user = contribs[gh_user]

                # Update contrib_type & packages contributed to in contribs file
                # Get list of existing contrib types
                existing_contribs = contribs_user["contributor_type"]
                contrib_key_yml = ppl_types[issue_review_role][0]
                review_role = clean_list(ppl_types[issue_review_role][1])

                # Get existing list of packages that they've worked on for role
                all_pkgs = contribs_user[contrib_key_yml]

                # If users's name is missing in issue, populate from contribs dict
                if issue_meta[issue_review_role]["name"] == "":
                    packages[pkg_name][issue_review_role]["name"] = contribs_user[
                        "name"
                    ]

                # Update package list in contrib file
                # TODO - make function
                contrib_pkg_list = clean_list(contribs[gh_user][contrib_key_yml])
                unique_vals, vals = unique_new_vals(contrib_pkg_list, [pkg_name])
                if unique_vals:
                    contrib_pkg_list += vals

                # Update contribute_type type list in contrib file
                contrib_type_key = clean_list(contribs[gh_user]["contributor_type"])
                unique_vals, vals = unique_new_vals(contrib_type_key, review_role)
                if unique_vals:
                    contrib_type_key += vals

    # Export to yaml
    process_contribs.clean_export_yml(contribs, "contribs.yml")
    process_contribs.clean_export_yml(packages, "packs.yml")


if __name__ == "__main__":
    main()
