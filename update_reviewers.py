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
# TODO: removing advisory for some reason
# not sure why just some were removed.

import pickle

import ruamel.yaml as yaml

from pyosmeta.contrib_review_meta import UpdateReviewMeta
from pyosmeta.contributors import ProcessContributors
from pyosmeta.file_io import YamlIO, read_text_file

API_TOKEN = read_text_file("token.txt")

# Load contributors dict from website (just for now)
with open("all_contribs.pickle", "rb") as f:
    contribs = pickle.load(f)

contrib_path = "contributors.yml"
review_path = "packages.yml"

# TODO: here i'm assuming the other two scripts have been run and there is a
# contributors and packages yml file... then this is run last - but i need to
# figure out something better...
# TODO: This also doesn't work because open_yml_file opens from a url not a single file
# file_obj = YamlIO()
# review_dict = file_obj.open_yml_file(review_path)
# contribs = file_obj.open_yml_file(contrib_path)
process_contribs = ProcessContributors([], [], API_TOKEN)

# Will see how this works if you can't pass the token...
updateMeta = UpdateReviewMeta()

# TODO: might be able to instantiate the class with this object
# as it will be needed
# Open packages.yml file - this contains review metadata
# TODO: this does NOT contain the package maintainers ... add this
with open(review_path, "r") as file:
    all_reviews = yaml.safe_load(file)

# Create dict: package name, reviewer and editor GH handle for each review
review_meta = updateMeta.create_review_meta_dict(all_reviews)


# TODO: if i revamp this workflow, then i'd have a gh username id and name so
# there is always a case insensitive id to use as a key
# Make sure all gh username keys are lowercase
contribs = {k.lower(): v for k, v in contribs.items()}

contrib_types = updateMeta.contrib_types
missing = []
# Loop through the review metadata item - (key)
for pkgname in review_meta:
    print("processing", pkgname)
    # Loop through each review role: editor, reviewers, author
    for issue_role in contrib_types:
        user_packages = []

        role = contrib_types[issue_role]
        gh_user = review_meta[pkgname][issue_role]["github_username"].lower().strip()
        # Add the package name to the editors list in contrib entry
        print(gh_user, user_packages)
        if gh_user in contribs.keys():
            user_packages = contribs[gh_user][role]
            user_packages = updateMeta.clean_pkg_list(user_packages)

            print(
                gh_user,
                "is already in our contrib database. Checking to see if the "
                "package is in their review contribution list.",
            )
            contribs[gh_user][role] = updateMeta.check_add_package(
                user_packages, pkgname
            )
        else:
            # User doesn't exist in contrib data yet add them
            # TODO: create method for this
            print(
                gh_user,
                "doesn't exist in our contributors yaml. Adding them now.",
            )
            new_user_dict = {}
            # TODO: if updateMeta inherits from contribs object how do i authenticate?
            new_user_dict = process_contribs.add_new_user(gh_user)
            contribs[gh_user] = new_user_dict[gh_user]
            # Then update their review process role w package name
            contribs[gh_user][role] = updateMeta.check_add_package([], pkgname)
            print(
                pkgname,
                "has been added to",
                gh_user,
                "'s list -",
                user_packages,
            )
            missing.append(gh_user)

# Turn contribs into list
contribs_list = updateMeta.dict_to_list(contribs)

final_yaml = "contributors.yml"
# Export to yaml
print("Saving updated contributors.yml file")
updateMeta.export_yaml(final_yaml, contribs_list)
updateMeta.clean_yaml_file(final_yaml)
