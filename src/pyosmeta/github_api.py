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
import time
from dataclasses import dataclass
from typing import Any, Optional, Union

import requests
from dotenv import load_dotenv


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

        Raises
        ------
        KeyError
            If the GITHUB_TOKEN environment variable is not found.
        """
        load_dotenv()
        try:
            return os.environ["GITHUB_TOKEN"]
        except KeyError:
            raise KeyError(
                "Oops! A GITHUB_TOKEN environment variable wasn't found."
            )

    @property
    def api_endpoint(self) -> str:
        """Create the API endpoint url

        Returns
        -------
        str
            A string representing the api endpoint to query.

        Notes
        -----
        The rest API will look for issues that have ALL labels provided in a
        query (using an AND query vs an OR query by default). The graphQL may
        support OR. As such if there is a list provided, we will want to parse
        down the returned list to only include issues with a specific label
        included.
        """
        # If there is more than one label provided, request all issues
        # Will have to parse later.
        if len(self.labels) > 1:
            url = (
                f"https://api.github.com/repos/{self.org}/{self.repo}/"
                f"issues?state=all&per_page=100"
            )
        else:
            url = (
                f"https://api.github.com/repos/{self.org}/{self.repo}/"
                f"issues?labels={self.labels[0]}&state=all&per_page=100"
            )
        return url

    def handle_rate_limit(self, response):
        """
        Handle rate limiting by waiting until the rate limit resets.

        Parameters
        ----------
        response : requests.Response
            The response object from the API request.

        Notes
        -----
        This method checks the remaining rate limit in the response headers.
        If the remaining requests are exhausted, it calculates the time
        until the rate limit resets and sleeps accordingly.
        """

        if "X-RateLimit-Remaining" in response.headers:
            remaining_requests = int(response.headers["X-RateLimit-Remaining"])
            if remaining_requests <= 0:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                sleep_time = max(reset_time - time.time(), 0) + 1
                time.sleep(sleep_time)

    def return_response(self) -> list[dict[str, object]]:
        """
        Make a GET request to the Github API endpoint
        Deserialize json response to list of dicts.

        Handles pagination as github has a REST api 100 request max.

        Returns
        -------
        list
            List of dict items each containing a review issue
        """

        results = []
        # This is computed as a property. Reassign here to support pagination
        # and new urls for each page
        api_endpoint_url = self.api_endpoint
        try:
            while True:
                response = requests.get(
                    api_endpoint_url,
                    headers={"Authorization": f"token {self.get_token()}"},
                )
                response.raise_for_status()
                results.extend(response.json())

                # Check if there are more pages to fetch
                if "next" in response.links:
                    next_url = response.links["next"]["url"]
                    api_endpoint_url = next_url
                else:
                    break

                # Handle rate limiting
                self.handle_rate_limit(response)

        except requests.HTTPError as exception:
            raise exception

        return results

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

    def get_user_info(
        self, gh_handle: str, name: Optional[str] = None
    ) -> dict[str, Union[str, Any]]:
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

        url = f"https://api.github.com/users/{gh_handle}"
        headers = {"Authorization": f"Bearer {self.get_token()}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise ValueError(
                "Oops, I couldn't authenticate. Please check your token."
            )
        return response.json()
