"""
A small module that supports updating reviewer metadata for contributions
related to peer review (Editors, Reviewers, Maintainers)
"""
from dataclasses import dataclass

from .contributors import ProcessContributors


@dataclass
class UpdateReviewMeta(ProcessContributors):
    def __init__(self):
        """
        Parameters
        ----------

        contrib_types : dict
            xxx
        """

        self.contrib_types = {
            "reviewer_1": "packages-reviewed",
            "reviewer_2": "packages-reviewed",
            "editor": "packages-editor",
            "submitting_author": "packages-submitted",
        }

    def _create_review_meta(self, areview: dict) -> dict:
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

    def create_review_meta_dict(self, all_reviews: dict) -> dict:
        """

        Parameters
        ----------
        all_reviews: dict
            dict containing all of the issue review metadata for pyos reviews

        Returns
        -------
            dict
            A dictionary containing only review package name, editors, reviewers &
            authors.

        """
        review_meta = {}
        for areview in all_reviews:
            review_meta[areview["package_name"]] = self._create_review_meta(areview)
        return review_meta

    def check_add_package(self, user_packages: list, pkgname: str) -> list:
        """Grabs the users list of packages and adds a new one
        (pkgname) if it already isn't in their list.

        Each user has a list of packages that they submitted,
        reviewer or served as editor for in the review. This
        takes a package and a list for a particular role and
        checks to see if the package needs to be added.
        """

        # TODO: Make sure package name is always lower case (Xclim for alex editor)
        # For this to work we will need to add a package-name and package-id to the
        # packages.yml file
        if pkgname.lower() in [x.lower() for x in user_packages]:
            print("All good -", pkgname, " is already there.")
        else:
            # If the package is not in the list, add it
            user_packages.append(pkgname)
            print(pkgname, "is missing from user's list. Adding it now.")
        return user_packages

    def clean_pkg_list(self, user_packages: str | list | None):
        """Helper method that cleans a list of user packages derived from a
        YAML file
        """
        if isinstance(user_packages, str):
            user_packages = [user_packages]
        if user_packages is None:
            user_packages = []
        # Remove any none's etc from the data
        user_packages = list(filter(lambda x: x, user_packages))
        return user_packages
