"""
A module that houses all of the methods related to interfacing
with the GitHub API. THere are three groupings of activities here:

1. Parsing github issues to return peer review information
2. Parsing contributor profile data to return names and affiliations where
available
3. Parsing package repositories to return package metadata such as pull request
numbers, stars and more "health & stability" related metrics
"""

import logging
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

        Returns
        -------
        list
            List of dict items each containing a review issue
        """

        try:
            response = requests.get(
                self.api_endpoint,
                headers={"Authorization": f"token {self.get_token()}"},
            )
            response.raise_for_status()

        except requests.HTTPError as exception:
            raise exception

        return response.json()

    def get_repo_meta(self, url: str) -> dict[str, Any] | None:
        """
        Get GitHub metrics from the GitHub API for a single repository.

        Parameters
        ----------
        url : str
            The URL of the repository.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the specified GitHub metrics for the repository.
            Returns None if the repository is not found or access is forbidden.

        Notes
        -----
        This method makes a GET call to the GitHub API to retrieve metadata
        about a pyos reviewed package repository.

        If the repository is not found (status code 404) or access is forbidden
        (status code 403), this method returns None.

        """

        # Get the url (normally the docs) and description of a repo
        response = requests.get(
            url, headers={"Authorization": f"token {self.get_token()}"}
        )

        # Check if the request was successful (status code 2xx)
        if response.ok:
            return response.json()

        # Handle specific HTTP errors
        elif response.status_code == 404:
            logging.warning(
                f"Repository not found: {url}. Did the repo URL change?"
            )
            return None
        elif response.status_code == 403:
            # Construct a single warning message with formatted strings
            warning_message = (
                "Oops! You may have hit an API limit for URL: {url}.\n"
                f"API Response Text: {response.text}\n"
                f"API Response Headers: {response.headers}"
            )
            logging.warning(warning_message)
            return None

        else:
            # Log other HTTP errors
            logging.warning(
                f"Unexpected HTTP error: {response.status_code} URL: {url}"
            )
            return None

    def get_repo_contribs(self, url: str) -> int | None:
        """
        Returns the count of total contributors to a repository.

        Parameters
        ----------
        url : str
            The URL of the repository.

        Returns
        -------
        int
            The count of total contributors to the repository.

        Notes
        -----
        This method makes a GET call to the GitHub API to retrieve
        total contributors for the specified repository. It then returns the
        count of contributors.

        If the repository is not found (status code 404), a warning message is
        logged, and the method returns None.
        """

        repo_contribs_url = url + "/contributors"

        # Get the url (normally the docs) and repository description
        response = requests.get(
            repo_contribs_url,
            headers={"Authorization": f"token {self.get_token()}"},
        )

        # Handle 404 error (Repository not found)
        if response.status_code == 404:
            logging.warning(
                f"Repository not found: {repo_contribs_url}. "
                "Did the repo URL change?"
            )
            return None
        # Return total contributors
        else:
            return len(response.json())

    def get_last_commit(self, repo: str) -> str:
        """Returns the last commit to the repository.

        Parameters
        ----------
        str : string
            A string containing a datetime object representing the datetime of
            the last commit to the repo

        Returns
        -------
        str
            String representing the timestamp for the last commit to the repo.
        """
        url = repo + "/commits"
        response = requests.get(
            url, headers={"Authorization": f"token {self.get_token()}"}
        ).json()
        date = response[0]["commit"]["author"]["date"]

        return date
