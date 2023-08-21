import json
import os
import re

import requests
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from typing import List, Optional, Set, Tuple, Union


class UrlValidatorMixin:
    # Check fields is false given mixin is used by two diff classes
    @field_validator(
        "website", "documentation", mode="before", check_fields=False
    )
    @classmethod
    def format_url(cls, url: str) -> str:
        """Append https to the beginning of URL if it doesn't exist & cleanup
        If the url doesn't have https add it
        If the url starts with http change it to https
        Else do nothing

        Parameters
        ----------
        url : str
            String representing the url grabbed from the GH api

        """

        if not url:
            return url  # Returns empty string if url is empty
        else:
            if url.startswith("http://"):
                print(f"{url} 'http://' replacing w 'https://'")
                url = url.replace("http://", "https://")
            elif not url.startswith("http"):
                print("Oops, missing http")
                url = "https://" + url
        if cls._check_url(url=url):
            return url
        else:
            return None

    @staticmethod
    def _check_url(url: str) -> bool:
        """Test url. Return true if there's a valid response, False if not

        Parameters
        ----------
        url : str
            String for a url to a website to test.

        """

        try:
            response = requests.get(url, timeout=6)
            return response.status_code == 200
        except Exception:
            print("Oops, url", url, "is not valid, removing it")
            return False


class PersonModel(BaseModel, UrlValidatorMixin):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    name: Optional[str] = None
    github_username: str = Field(None, validation_alias=AliasChoices("login"))
    github_image_id: int = Field(None, validation_alias=AliasChoices("id"))
    title: Optional[Union[list[str], str]] = None
    sort: Optional[int] = None
    bio: Optional[str] = None
    organization: Optional[str] = Field(
        None, validation_alias=AliasChoices("company")
    )
    date_added: Optional[str] = ""
    deia_advisory: Optional[bool] = False
    editorial_board: Optional[bool] = Field(
        None, validation_alias=AliasChoices("editorial-board")
    )
    advisory: Optional[bool] = False
    twitter: Optional[str] = Field(
        None, validation_alias=AliasChoices("twitter_username")
    )
    mastodon: Optional[str] = Field(
        None, validation_alias=AliasChoices("mastodon_username", "mastodon")
    )
    orcidid: Optional[str] = None
    website: Optional[str] = Field(
        None, validation_alias=AliasChoices("blog", "website")
    )
    board: Optional[bool] = False
    contributor_type: Set[str] = set()
    packages_editor: Set[str] = set()
    packages_submitted: Set[str] = set()
    packages_reviewed: Set[str] = set()
    location: Optional[str] = None
    email: Optional[str] = None

    @field_validator(
        "packages_reviewed",
        "packages_submitted",
        "packages_editor",
        "contributor_type",
        mode="before",
    )
    @classmethod
    def convert_to_set(cls, value: list[str]):
        if isinstance(value, list):
            if not value:
                return set()
            elif value[0] is None:
                return set()
            else:
                value = [a_val.lower() for a_val in value]
                return set(value)
        elif value is None:
            return set()
        return set(value.lower())

    def add_unique_value(self, attr_name: str, values: Union[str, list[str]]):
        """A helper that will add only unique values to an existing list"""
        if isinstance(values, str):
            values = [values]
        attribute = getattr(self, attr_name)
        if isinstance(attribute, set):
            attribute.update(values)
        else:
            raise ValueError(f"{attr_name} is not a set attribute")

    @field_serializer(
        "packages_reviewed",
        "packages_submitted",
        "packages_editor",
        "contributor_type",
    )
    def serialize_set(self, items: Set[str]):
        """This is a serializer that runs on export. It ensures sets are
        converted to lists"""
        return sorted(list(items))

    @field_validator("bio", mode="before")
    @classmethod
    def clean_strings(cls, string: str) -> str:
        """This is a cleaning step that will remove spurious
        characters from string fields.

        """
        if isinstance(string, str):
            string = re.sub(r"[\r\n]", "", string)
        return string


@dataclass
class ProcessContributors:
    """A class that contains some basic methods to support populating and
    updating contributor data."""

    def __init__(self, json_files: List) -> None:
        """
        Parameters
        ----------

        json_files : list
            A list of string objects each of which represents a URL to a JSON
            file to be parsed
        GITHUB_TOKEN : str
            A string containing your API token needed to access the github API
        """

        self.json_files = json_files
        # self.GITHUB_TOKEN = GITHUB_TOKEN
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

        self.contrib_types = {
            "reviewer_1": ["packages_reviewed", ["reviewer", "peer-review"]],
            "reviewer_2": ["packages_reviewed", ["reviewer", "peer-review"]],
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

    def get_token(self) -> str:
        """Fetches the GitHub API key from the users environment. If running
        local from an .env file.

        Returns
        -------
        str
            The provided API key in the .env file.
        """
        load_dotenv()
        return os.environ["GITHUB_TOKEN"]

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

        if "software-peer-review" in json_file:
            contrib_type = "peer-review-guide"
        elif "python-package-guide" in json_file:
            contrib_type = "package-guide"
        elif "pyopensci.github.io" in json_file:
            contrib_type = "web-contrib"
        elif "update-web-metadata" in json_file:
            contrib_type = "code-contrib"
        else:
            contrib_type = "community"
        return contrib_type

    # TODO possibly could repurpose this as a check in the code
    # but it should return get_user_info
    # def check_add_user(self, gh_user: str, contribs: Dict[str, str]) -> None:
    #     """Check to make sure user exists in the existing contrib data. If
    #     they
    #     don't' exist, add them

    #     Parameters
    #     ----------
    #     gh_user : str
    #         github username
    #     contribs: dict
    #         A dictionary containing contributors with gh user being the key

    #     This returns the updated dictionary with a new user at the end.

    #     """
    #     if gh_user not in contribs.keys():
    #         print("Missing user", gh_user, "adding them now.")
    #         return self.get_user_info(gh_user)

    def load_json(self, json_path: str) -> dict:
        """
        Helper function that deserializes a json file to a dict.

        """
        try:
            response = requests.get(json_path)
        except Exception as ae:
            print(ae)
        return json.loads(response.text)

    # TODO: check is i'm using the contrib type part of this method ?
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

        # TODO: to make this faster, it might be better to return a dict
        # with username : [contrib1, contrib2]
        for json_file in self.json_files:
            # Process the JSON file and add the data to the combined dictionary
            try:
                key, users = self.process_json_file(json_file)
                combined_data[key] = users
            except Exception as e:
                print("Oops - can't process", json_file, e)
        return combined_data

    def get_user_info(
        self, username: str, aname: Optional[str] = None
    ) -> dict:
        """
        Get a single user's information from their GitHub username using the
        GitHub API
        # https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#get-the-authenticated-user

        Parameters
        ----------
        username : string
            Github username to retrieve data for
        aname : str default=None
            A user's name from the contributors.yml file.
            https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#get-a-user

        Returns
        -------
            Dict with updated user data grabbed from the GH API
        """

        url = f"https://api.github.com/users/{username}"
        headers = {"Authorization": f"Bearer {self.get_token()}"}
        response = requests.get(url, headers=headers)
        # TODO: add check here for if credentials are bad
        # if message = Bad credentials
        response_json = response.json()

        # TODO: make an attribute and call it here?
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
                webDict[gh_user][
                    "contributor_type"
                ] = self._update_contrib_type(
                    webDict[gh_user]["contributor_type"],
                    repoDict[gh_user]["contributor_type"],
                )

            # If the user is not in the web dict, add them
            else:
                print("New user found. Adding: ", gh_user)
                webDict[gh_user] = repoDict[gh_user]
        return webDict
