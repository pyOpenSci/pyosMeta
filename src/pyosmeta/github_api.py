"""
A module that houses all of the methods related to interfacing
with the GitHub API. THere are three groupings of activities here:

1. Parsing github issues to return peer review information
2. Parsing contributor profile data to return names and affiliations where
available
3. Parsing package repositories to return package metadata such as pull request
numbers, stars and more "health & stability" related metrics
"""

import os

import requests
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Any


@dataclass
class GitHubAPI:
    """
    A class that processes GitHub issues in our peer review process and returns
    metadata about each package.
    """

    def __init__(
        self,
        org: str | None = None,
        repo: str | None = None,
        labels: list[str] | None = None,
    ):
        """
        Initialize a GitHub client object that handles interfacing with the
        GitHub API.

        Parameters
        ----------
        org : str, Optional
            Organization name where the issues exist
        repo : str, Optional
            Repo name where the software review issues live
        labels : list of strings, Optional
            Labels for issues that we want to access - e.g. pyos approved
        """

        self.org: str | None = org
        self.repo: str | None = repo
        self.labels: list[str] | None = labels

    def get_token(self) -> str | None:
        """Fetches the GitHub API key from the users environment. If running
        local from an .env file.

        Returns
        -------
        str
            The provided API key in the .env file.
        """
        load_dotenv()
        return os.environ["GITHUB_TOKEN"]

    @property
    def api_endpoint(self):
        labels_query = ",".join(self.labels) if self.labels else ""
        url = (
            f"https://api.github.com/repos/{self.org}/{self.repo}/"
            f"issues?labels={labels_query}&state=all&per_page=100"
        )
        return url

    def return_response(self) -> list[dict[str, object]]:
        """
        Make a GET request to the Github API endpoint
        Deserialize json response to list of dicts.

        Parameters
        ----------
        username : str
            GitHub username of person authenticating to hit the GitHub API

        Returns
        -------
        list
            List of dict items each containing a review issue
        """
        print(self.api_endpoint)

        try:
            response = requests.get(
                self.api_endpoint,
                headers={"Authorization": f"token {self.get_token()}"},
            )
            response.raise_for_status()

        except requests.HTTPError as exception:
            raise exception

        return response.json()

    # This is also github related
    def get_repo_meta(self, url: str) -> dict[str, Any]:
        """
        Returns a set of GH stats from each repo of our reviewed packages.

        """
        # stats_dict = {}
        # Get the url (normally the docs) and description of a repo
        response = requests.get(
            url, headers={"Authorization": f"token {self.get_token()}"}
        )

        # TODO: should this be some sort of try/except how do i catch these
        # Response errors in the best way possible?
        if response.status_code == 404:
            print("Can't find: ", url, ". Did the repo url change?")
        elif response.status_code == 403:
            print("Oops you may have hit an API limit. Exiting")
            print(f"API Response Text: {response.text}")
            print(f"API Response Headers: {response.headers}")
            exit()

        else:
            return response.json()

    def get_repo_contribs(self, url: str) -> dict:
        """
        Returns a count for total contribs to a repo.
        I definitely think graphQL would be better suited for these calls
        """
        repo_contribs = url + "/contributors"
        # Get the url (normally the docs) and repository description
        response = requests.get(
            repo_contribs,
            headers={"Authorization": f"token {self.get_token()}"},
        )

        if response.status_code == 404:
            print("Can't find: ", repo_contribs, ". Did the repo url change?")
        # Extract the description and homepage URL from the JSON response
        else:
            return len(response.json())

    def get_last_commit(self, repo: str) -> str:
        """Returns the last commit to the repository.

        Parameters
        ----------
        str : string
            A string containing a datetime object representing the datetime of
            the last commit to the repo
        """
        url = repo + "/commits"
        response = requests.get(
            url, headers={"Authorization": f"token {self.get_token()}"}
        ).json()
        date = response[0]["commit"]["author"]["date"]

        return date
