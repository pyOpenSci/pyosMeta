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


with open(review_path, "r") as file:
    review_list = yaml.safe_load(file)

# Get list of package name, reviewer and editor GH handle for each review
# Go through each review item and get the gh username of the submitting author
review_meta = {}
for areview in review_list:
    review_meta[areview["package_name"]] = {
        "submitting_author": areview["submitting_author"],
        "editor": areview["editor"],
        "reviewer_1": areview["reviewer_1"],
        "reviewer_2": areview["reviewer_2"],
    }

# Load contribs dict  (just for now)
with open("all_contribs.pickle", "rb") as f:
    contribs = pickle.load(f)

# TODO: make loop below function

# def check_review_meta(review_meta, pkgname, contrib_type, contrib_dict):
#     gh_user = review_meta[pkgname]["submitting_author"]["github_username"]

#     # To do this can be a list or dict?
#     contrib_type = "packages-submitted"
#     if pkgname in contrib_dict[gh_user][contrib_type]:
#         print("It's already there! No need to update")
#     else:
#         contrib_dict[gh_user][contrib_type].append(pkgname)
#         print("Adding", pkgname, "to " gh_user, "for ", contrib_type)

# Loop through each issue and get editors, reviewers and authors
# then add them to the contrib data as needed
# TODO: if these are new contributors then i need a check to look for that too
# Running into issues not with gh usernames having caps
# people don't use those consistently so make all usernames lower


# Make sure all gh usernames are lower
contribs = {k.lower(): v for k, v in contribs.items()}

# TODO: how to handle two reviewers but the key is the same?
contrib_types = {
    "reviewer_1": "packages-reviewed",
    "reviewer_2": "packages-reviewed",
    "editor": "packages-editor",
    "submitting_author": "packages-submitted",
}
# contrib_type = contrib_types[2]
# TODO: this isn't working as expected. if the package name has caps it won't find it
# So i need to do a case insensitive check for it being in the list
user_packages = []


# TODO: should i use returns for each if clause?
def check_add_package(user_packages, pkgname) -> list:
    print("Yay", gh_user, "is already there")
    # user_packages = contribs[gh_user][role]
    # If there is no data, then just add the package
    if len(user_packages) == 0 or user_packages[0] == None:
        user_packages = [pkgname]
        print(
            "No packages for",
            role,
            " exist yet for",
            gh_user,
            "- adding:",
            pkgname,
        )
    # If there is data there, check for the package name
    elif pkgname.lower() in [p.lower() for p in user_packages]:
        print("All good - the package is already there")
    else:
        user_packages.append(pkgname)

    return user_packages


template_user = {
    "name": "",
    "bio": "",
    "organization": "",
    "title": "",
    "github_username": "",
    "github_image_id": "",
    "editorial-board": "",
    "twitter": "",
    "mastodon": "",
    "orcidid": "",
    "website": [],
    "contributor_type": [],
    "packages-editor": [],
    "packages-submitted": [],
    "packages-reviewed": [],
    "location": [],
    "email": [],
}

update_keys = [
    "twitter",
    "website",
    "location",
    "bio",
    "organization",
    "email",
    "name",
]

missing = []
# Loop through the review metadata - (key), editor, reviewers, author
for pkgname in review_meta:
    print("processing", pkgname)
    # Now for each package review, get the editor
    role = "packages-editor"
    # TODO - now replace this with a loop that goes through each contrib type
    issue_role = "editor"
    # Get the gh username for the editor
    gh_user = review_meta[pkgname][issue_role]["github_username"].lower()
    # If the user already exists in contrib data, then add the package name
    # to the editors list in their contrib entry
    if gh_user in contribs.keys():
        user_packages = contribs[gh_user][role]
        contribs[gh_user][role] = check_add_package(user_packages, pkgname)
    else:
        # User doesn't exist in contrib data yet add them
        # TODO: create method for this
        new = {}
        new[gh_user] = template_user
        # Get updated info from gh
        # TODO: because i'm using this object for other things, consider just
        # populating attributes rather than instantiating them ?
        gh_obj = ProcessContributors([], [], API_TOKEN)
        gh_data = gh_obj.get_gh_data([gh_user], API_TOKEN)
        update = gh_obj.update_contrib_data(new, gh_data, update_keys)
        # Finally add them to the contrib data
        contribs.update(update)
        # Then update their role
        contribs[gh_user][role] = check_add_package([], pkgname)

        missing.append(gh_user)
        print(
            "Oops - the user",
            gh_user,
            "doesn't exist in the data yet - need to add",
        )

user = "arianesasso"
user = "jbencook"
contribs[user][role]

# This is the workflow to add a new person getting their data from
# Gh
