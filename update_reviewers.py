"""
Parse the updated review and contributor data.
Make sure each contributor has the packages they've served
as reviewer or editor for.
Add a new person if they don't exist in the contributor
file.
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
# process_contribs = ProcessContributors([], [], API_TOKEN)
process_contribs = ProcessContributors([], [], API_TOKEN)

# Open packages.yml
with open(review_path, "r") as file:
    all_reviews = yaml.safe_load(file)


def create_review_meta(areview):
    """
    Generate a dictionary entry for a single review with
    the submitting author, editor and both reviewers.

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

# TODO: make loop below function
# TODO: if these are new contributors then i need a check to look for that too
# Running into issues not with gh usernames having caps
# people don't use those consistently so make all usernames lower

# Make sure all gh username keys are lowercase
contribs = {k.lower(): v for k, v in contribs.items()}

# contrib_type = contrib_types[2]
# TODO: this isn't working as expected. if the package name has caps it won't find it
# So i need to do a case insensitive check for it being in the list


# TODO: should i use returns for each conditional section?
# TODO: move to contribs class as method?
def check_add_package(user_packages, pkgname) -> list:
    """Grabs the users list of packages and adds a new one
    (pkgname) if it already isn't in their list.

    Each user has a list of packages that they submitted,
    reviewer or served as editor for in the review. This
    takes a package and a list for a particular role and
    checks to see if the package needs to be added.
    """
    print(gh_user, "is already in our contrib database!")
    # user_packages = contribs[gh_user][role]
    # If there is no data, then just add the package

    # TODO: there is probably a cleaner way to implement this
    if user_packages is None or len(user_packages) == 0 or user_packages[0] == None:
        print(
            "No packages for",
            role,
            " exist yet for",
            gh_user,
            "- adding:",
            pkgname,
        )
        return [pkgname]
    # If use has an entry, check to see if the package name is there
    # If there is only a single package, then do nothing
    elif user_packages == pkgname:
        return print("All good - the package is already there")
    elif pkgname.lower() in [p.lower() for p in user_packages]:
        return print("All good - the package is already there")
    else:
        return user_packages.append(pkgname)


# TODO: how to handle two reviewers but the key is the same?
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
    print("processing", pkgname)

    # Loop through each review role: editor, reviewers, author
    for issue_role in contrib_types:
        user_packages = []
        # Now for each package review, get the editor
        role = contrib_types[issue_role]
        # Get the gh username
        gh_user = review_meta[pkgname][issue_role]["github_username"].lower().strip()
        # Add the package name to the editors list in contrib entry
        print(gh_user)
        if gh_user in contribs.keys():
            user_packages = contribs[gh_user][role]
            # TODO : do a case sensitive check for the package here
            # And update it to have case if it does...
            contribs[gh_user][role] = check_add_package(user_packages, pkgname)
        else:
            # User doesn't exist in contrib data yet add them
            # TODO: create method for this
            print(
                gh_user,
                "doesn't exist in our contributors yaml. Adding them now.",
            )
            new_user_dict = {}
            # TODO: For some reason this method
            # is updating the c-thoben key with robaina's information?
            # in the contribs dictionary which is never passed to it - why?
            new_user_dict = process_contribs.add_new_user(gh_user)
            contribs[gh_user] = new_user_dict[gh_user]
            # Then update their review process role w package name
            contribs[gh_user][role] = check_add_package([], pkgname)
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
