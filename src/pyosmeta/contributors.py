import json
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import requests

from .github_api import GitHubAPI
from .logging import logger


@dataclass
class ProcessContributors:
    """A class that contains some basic methods to support populating and
    updating contributor data."""

    def __init__(self, github_api: GitHubAPI, json_files: List) -> None:
        """
        Parameters
        ----------
        github_api : str
            Instantiated instance of a GitHubAPI object
        json_files : list
            A list of string objects each of which represents a URL to a JSON
            file to be parsed
        """

        self.github_api = github_api
        self.json_files = json_files

        self.update_keys = [
            "twitter",
            "website",
            "location",
            "bio",
            "organization",
            "email",
            "name",
            "github_image_id",
            "github_username",
        ]

        """A dictionary that maps a category type found in our peer review
        submission template to the roles and role categories that a contributor
        should have populated associated with the review in the contributors.yml

        example
        reviewers is in the software submission template like this:
        reviewers: @username, @username2
        Being a reviewer maps to two roles in the users contributions to
        pyOpenSci: reviewer and peer-review
        packages_reviewed is another item in the contributors file that lists
        all of the packages that user has reviewed. So if they ar e
        """
        self.contrib_types = {
            "eic": ["packages_eic", ["eic", "peer-review"]],
            "reviewers": ["packages_reviewed", ["reviewer", "peer-review"]],
            "editor": ["packages_editor", ["editor", "peer-review"]],
            "submitting_author": [
                "packages_submitted",
                ["maintainer", "submitting-author", "peer-review"],
            ],
            "all_current_maintainers": [
                "packages_submitted",
                ["maintainer", "peer-review"],
            ],
        }

    def check_contrib_type(self, json_file: str):
        """
        Determine the type of contribution the person
        has made based upon which repo the all contribs json
        file lives in.

        Parameters
        ----------
        json_file: str
            Path to the json file on GitHub produced by the all-contribs
            bot.

        Returns
        -------
        str
            Contribution type.
        """

        if any(
            key in json_file
            for key in ["software-submission", "software-peer-review"]
        ):
            # TODO: change this to programs - peer review
            contrib_type = "peer-review-guide"
        elif any(
            key in json_file
            for key in [
                "python-package-guide",
                "pyosPackage",
                "pyos-package-template",
            ]
        ):
            # TODO consider change this to python-packaging
            contrib_type = "package-guide"
        # TODO: technically packaging guide is open-education too
        elif "lessons" in json_file:
            contrib_type = "open-education"
        elif "pyopensci.github.io" in json_file:
            contrib_type = "web-contrib"
        elif "pyosMeta" in json_file or "metrics" in json_file:
            contrib_type = "code-contrib"
        else:
            contrib_type = "community"
        return contrib_type

    # Possibly github it is a get request but it says json path
    def load_json(self, json_path: str) -> dict:
        """
        Helper function that deserializes a json file to a dict.

        """
        try:
            response = requests.get(json_path)
        except Exception:
            logger.error(
                f"Error loading json file: {json_path}", exec_info=True
            )
        return json.loads(response.text)

    def process_json_file(self, json_file: str) -> Tuple[str, List]:
        """Deserialize a JSON file from a URL and cleanup data

        Open a JSON file containing contributor data created from a
        all-contributors json file.
        Collect the contribution type and all users associated with that
        contribution
        Return a contrib type and list of users

        Parameters
        ----------
        json_file : string
            Web url of a json formatted file

        """

        data = self.load_json(json_file)
        contrib_type = self.check_contrib_type(json_file)

        all_users = []
        for entry in data["contributors"]:
            all_users.append(entry["login"].lower())

        return contrib_type, all_users

    def combine_json_data(self) -> dict:
        """Deserialize and clean a list of json file url's.

        Parses a list of json file  urls representing all-contributor bot
        json files.

        Returns
        -------
            Dictionary containing json data for all contributors across
            the website
        """
        # Create an empty dictionary to hold the combined data
        combined_data = {}

        for json_file in self.json_files:
            # Process the JSON file and add the data to the combined dictionary
            try:
                key, users = self.process_json_file(json_file)
                combined_data[key] = users
            except Exception:
                logger.error(
                    f"Oops - can't process: {json_file}", exc_info=True
                )
        return combined_data

    def return_user_info(
        self, gh_handle: str, name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get a single user's information from their GitHub username using the
        GitHub API
        # https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#get-the-authenticated-user

        Parameters
        ----------
        gh_handle : string
            Github username to retrieve data for
        name : str default=None
            A user's name from the contributors.yml file.
            https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#get-a-user

        Returns
        -------
            Dict with updated user data grabbed from the GH API
        """

        response_json = self.github_api.get_user_info(gh_handle, name)

        update_keys = {
            "name": "name",
            "location": "location",
            "email": "email",
            "bio": "bio",
            "twitter": "twitter_username",
            "mastodon": "mastodon_username",
            "organization": "company",
            "website": "blog",
            "github_image_id": "id",
            "github_username": "login",
        }

        user_data = {}
        for key in update_keys:
            user_data[key] = response_json.get(update_keys[key], None)

        return user_data

    def _update_contrib_type(
        self, webContribTypes: List, repoContribTypes: List
    ) -> list:
        """
        Compares contrib types for a single gh user from the website to
        what's in the all-contributor bot .json dict. Adds any new contrib
        types to the user's list if there are any.

        Parameters
        ----------
        webContribTypes : list
            List of contrib types populated from
            `webDict[gh_user]["contributor_type"]`

        repoContribTypes : list
            List populated from `repoDict[gh_user]["contributor_type"]`

        Returns
        -------
        list:
            List of updated contribution types for a specific user.

        """
        if webContribTypes is None:
            return repoContribTypes
        else:
            existing_contribs = set(webContribTypes)
            new_contribs = set(repoContribTypes)
            missing = list(sorted(new_contribs - existing_contribs))

            return webContribTypes + missing

    def combine_users(self, repoDict: dict, webDict: dict) -> dict:
        """
        Method that combines website yaml users with contribs across
        other repos into a single dictionary.

        NOTE: this method also currently checks contrib data and updates it
        for existing users. This is likely a method that could stand alone.
        This method in general should be broken down into simpler parts.

        Parameters
        ----------
        repoDict: dict
            Dictionary representing the deserialized json data contained
            in the all-contributors .json file located in each of our
            repositories.

        webDict: dict
            Dictionary representing the deserialized YAML data parsed from
            the website YAML contributors file.

        Returns
        -------
        dict :
            Dictionary containing the users from the website combined with
            new users pulled from the all-contribs bot .json files.
            This dict also contains updated contribution types for each user.
        """

        for gh_user in repoDict.keys():
            if gh_user in webDict.keys():
                # Return a list of updated contributor type keys and use it to
                # update the web dict
                webDict[gh_user]["contributor_type"] = (
                    self._update_contrib_type(
                        webDict[gh_user]["contributor_type"],
                        repoDict[gh_user]["contributor_type"],
                    )
                )

            # If the user is not in the web dict, add them
            else:
                logger.info(f"New user found. Adding: {gh_user}")
                webDict[gh_user] = repoDict[gh_user]
        return webDict
