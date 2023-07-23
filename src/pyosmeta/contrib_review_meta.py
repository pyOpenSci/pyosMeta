"""
DELETE ME!
A small module that supports updating reviewer metadata for contributions
related to peer review (Editors, Reviewers, Maintainers)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from .contributors import ProcessContributors

# @dataclass
# class UpdateReviewMeta(ProcessContributors):
#     """This is a class that is designed to add additional functionality
#     to ProcessContribs to support updating reviewer metadata associated with
#     review issues. It is a bridge between the ProcessContributors and
#     ProcessReviews objects."""

#     def __init__(self, GITHUB_TOKEN):
#         """
#         Parameters
#         ----------

#         GITHUB_TOKEN : str
#             GitHub token string
#         """
#         super().__init__(self, GITHUB_TOKEN)

#     #     # This object and the object below are the only unique things
#     #     # in this class
#     #     self.contrib_types = {
#     #         "reviewer_1": ["packages-reviewed", ["reviewer", "peer-review"]],
#     #         "reviewer_2": ["packages-reviewed", ["reviewer", "peer-review"]],
#     #         "editor": ["packages-editor", ["editor", "peer-review"]],
#     #         "submitting_author": [
#     #             "packages-submitted",
#     #             ["maintainer", "submitting-author", "peer-review"],
#     #         ],
#     #         "all_current_maintainers": [
#     #             "packages-submitted",
#     #             ["maintainer", "peer-review"],
#     #         ],
#     #     }

#     # # def refresh_contribs(self, contribs: Dict, new_contribs, review_role):
#     # #     contrib_types = self.contrib_types
#     # #     contrib_key_yml = ""
#     # #     # Contributor type will be updated which is a list of roles
#     # #     if new_contribs:
#     # #         contrib_key_yml = contrib_types[review_role][0]
#     # #         existing_contribs = contribs[contrib_key_yml]
#     # #     # Else this is a specific review role meant to update package list
#     # #     else:
#     # #         new_contribs = contrib_types[review_role][1]
#     # #         existing_contribs = contribs["contributor_type"]

#     # #     final_list = self.update_contrib_list(existing_contribs, new_contribs)
#     # #     return (contrib_key_yml, final_list)

# # TODO - update_contrib_list does the same thing
# def check_add_package(self, user_packages: list, pkgname: str) -> list:
#     """Grabs the users list of packages and adds a new one
#     (pkgname) if it already isn't in their list.

#     Each user has a list of packages that they submitted,
#     reviewer or served as editor for in the review. This
#     takes a package and a list for a particular role and
#     checks to see if the package needs to be added.
#     """

#     # TODO: Make sure package name is always lower case (Xclim for alex editor)
#     # For this to work we will need to add a package-name and package-id to the
#     # packages.yml file
#     if pkgname.lower() in [x.lower() for x in user_packages]:
#         print("All good -", pkgname, " is already there.")
#     else:
#         # If the package is not in the list, add it
#         user_packages.append(pkgname)
#         print(pkgname, "is missing from user's list. Adding it now.")
#     return user_packages

# # TODO: remove - Can use clean_list here instead
# def clean_pkg_list(self, user_packages: str | list | None):
#     """Helper method that cleans a list of user packages derived from a
#     YAML file
#     """
#     if isinstance(user_packages, str):
#         user_packages = [user_packages]
#     if user_packages is None:
#         user_packages = []
#     # Remove any none's etc from the data
#     user_packages = list(filter(lambda x: x, user_packages))
#     return user_packages
