"""
Parse the updated review and contributor data.
Make sure each contributor has the packages they've served
as reviewer or editor for.
Add a new person if they don't exist in the contributor
file.

Right now this script is pulling from a contributor pickle file
creating in the parse-contributors.py file. However it might be better
to integrate the three scripts at some point.

To run:
python3 update_reviewers.py
"""

import pickle

import ruamel.yaml as yaml

from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import YamlIO

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)

contrib_path = "contributors.yml"
review_path = "packages.yml"

# file_obj = YamlIO()
# # first open the packages file and get a dict of
# # package name, reviewers and editors
# # TODO: this isn't working because we need to open a file
# # but in the end it will be a website path
# review_dict = file_obj.open_yml_file(review_path)
# contrib_dict = file_obj.open_yml_file(contrib_path)
process_contribs = ProcessContributors([], [], API_TOKEN)

# Open packages.yml
with open(review_path, "r") as file:
    all_reviews = yaml.safe_load(file)


def create_review_meta(areview: dict) -> dict:
    """
    Generate a dictionary entry for a single review with
    the submitting author, editor and both reviewers.

    Parameters
    ----------
    areview : dict
        A dictionary containing all of the metadata for a package parsed
        from the GitHub Issue.

    Returns
    -------
        Dict
        Dictionary containing just the submitting author, editor and reviews
        for a package review.
    """

    return {
        "submitting_author": areview["submitting_author"],
        "editor": areview["editor"],
        "reviewer_1": areview["reviewer_1"],
        "reviewer_2": areview["reviewer_2"],
    }


# Get list of package name, reviewer and editor GH handle for each review
# Go through each review item and get the gh username of the submitting author
review_meta = {}
for areview in all_reviews:
    review_meta[areview["package_name"]] = create_review_meta(areview)

# Load contributors dict  (just for now)
with open("all_contribs.pickle", "rb") as f:
    contribs = pickle.load(f)

# TODO: Right now people who have submitted or already have packages for
# their name - the packages are being removed

# Make sure all gh username keys are lowercase
contribs = {k.lower(): v for k, v in contribs.items()}


# LEFT OFF HERE - on agustina - agustina i think reviewed xclim?


# TODO: possibly use typing to allow for list, str or None ?
def check_add_package(user_packages: list | str, pkgname: str) -> list:
    """Grabs the users list of packages and adds a new one
    (pkgname) if it already isn't in their list.

    Each user has a list of packages that they submitted,
    reviewer or served as editor for in the review. This
    takes a package and a list for a particular role and
    checks to see if the package needs to be added.
    """
    print(
        gh_user,
        "is already in our contrib database. Checking to see if the "
        "package is in their review contribution list.",
    )
    # TODO: not sure if this is the best way to do this
    try:
        if user_packages.lower() == pkgname.lower():
            print("All good - The package is already in the", gh_user, "'s list")
            user_packages = [pkgname]
        else:
            pass
            # Otherwise add the new package to the users list of packages
            user_packages = [user_packages].append(pkgname)
            print(pkgname, "is missing from ", gh_user, "'s list. Adding it now.")
    except AttributeError as ae:
        print("The input is NOT a string - processing as a list")
        # If user packages is none, then add package name to a list
        if user_packages is None:
            user_packages = [pkgname]
            print(pkgname, "is missing from ", gh_user, "'s list. Adding it now.")
        # If user packages is in the existing list of packages, return the list
        elif pkgname.lower() in [x.lower() for x in user_packages]:
            print("All good -", pkgname, " is already there.")
            return user_packages
        # If the package is not in the list, then add it
        else:
            user_packages.append(pkgname)
            print(pkgname, "is missing from ", gh_user, "'s list. Adding it now.")
    return user_packages


contrib_types = {
    "reviewer_1": "packages-reviewed",
    "reviewer_2": "packages-reviewed",
    "editor": "packages-editor",
    "submitting_author": "packages-submitted",
}

missing = []
# Loop through the review metadata item - (key)
# TODO: when the user has no packages it returns contributor_type: []
# we don't want the [] in the yaml file it also adds *id001 to the entry...
for pkgname in review_meta:
    # breakpoint()
    # pkgname = "xclim"
    print("processing", pkgname)
    # Loop through each review role: editor, reviewers, author
    for issue_role in contrib_types:
        # issue_role = "editor"
        print(issue_role)

        user_packages = []
        # Now for each package review, get the editor
        role = contrib_types[issue_role]
        # Get the gh username
        gh_user = review_meta[pkgname][issue_role]["github_username"].lower().strip()
        # Add the package name to the editors list in contrib entry
        print(gh_user, user_packages)
        if gh_user in contribs.keys():
            user_packages = contribs[gh_user][role]

            # This is in a try/except because if the returned value is a single
            # value it will be a string. or it could be empty.
            try:
                # In the yaml sometimes there is a - with no data.
                # this returns a list with a value of None in it.
                # clean that list to be empty
                if user_packages[0] is None:
                    user_packages = []
            except:
                pass
            # 3 scenarios
            # 1. list of packages, check if package is there, append
            # 2. no packages - None create and return a list of 1 package name
            # 3. single package - this will return as a string.
            # TODO: this is weirdly
            contribs[gh_user][role] = check_add_package(user_packages, pkgname)
        else:
            # User doesn't exist in contrib data yet add them
            # TODO: create method for this
            print(
                gh_user,
                "doesn't exist in our contributors yaml. Adding them now.",
            )
            new_user_dict = {}
            new_user_dict = process_contribs.add_new_user(gh_user)
            contribs[gh_user] = new_user_dict[gh_user]
            # Then update their review process role w package name
            contribs[gh_user][role] = check_add_package([], pkgname)
            print(
                pkgname,
                "has been added to",
                gh_user,
                "'s list -",
                user_packages,
            )
            missing.append(gh_user)


# with open("all_contribs.pickle", "rb") as f:
#     contribs = pickle.load(f)
# Turn contribs into list
contribs_list = process_contribs.dict_to_list(contribs)

final_yaml = "contributors.yml"
# Export to yaml
process_contribs.export_yaml(final_yaml, contribs_list)
process_contribs.clean_yaml_file(final_yaml)


# This is the workflow to add a new person getting their data from
# Gh
# with open("all_contribs.pickle", "rb") as f:
#     contribs = pickle.load(f)
