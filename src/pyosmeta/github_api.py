"""
A module that contains all of the methods related to interfacing
with the GitHub API. There are three groupings of activities:

1. Parsing GitHub issues to return pyOS software peer review information
2. Parsing contributor profile data to return names and affiliations where
available
3. Parsing package repositories to return package metadata such as pull request
numbers, stars and more "health & stability" related metrics
"""

import os
import time
from dataclasses import dataclass
from typing import Any, Optional, Union

import requests
from dotenv import load_dotenv

from pyosmeta.models import ReviewModel

from .logging import logger


@dataclass
class GitHubAPI:
    """
    A class that processes GitHub issues in our peer review process and returns
    metadata about each package.
    """

    def __init__(
        self,
        org: str | None = "pyopensci",
        repo: str | None = None,
        labels: list[str] | None = None,
        endpoint_type: str = "issues",
        after_date: str = None,
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
            Labels for issues that we want to access - e.g. pyOS approved
        endpoint_type : str
            The end point type to hit (pull request -- pulls or issues).
            Default is "issues".
        """

        self.org: str | None = org
        self.repo: str | None = repo
        self.labels: list[str] | None = labels
        self.endpoint_type: str = endpoint_type
        # ISO 8601 format YYYY-MM-DDTHH:MM:SSZ.
        # using the api since query which represents updated at not created_at
        self.after_date: str = after_date

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
        support the OR param.
        """
        base_url = f"https://api.github.com/repos/{self.org}/{self.repo}/{self.endpoint_type}"
        params = ["state=all", "per_page=100"]

        # If there is more than one label provided, request all issues
        if self.labels:
            if len(self.labels) == 1:
                params.append(f"labels={self.labels[0]}")
        if self.after_date:
            # Check if the after date is in the correct format (YYYY-MM-DD)
            try:
                time.strptime(self.after_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "Invalid after date format. Please use YYYY-MM-DD."
                )

            params.append(f"since={self.after_date}")

        return f"{base_url}?{'&'.join(params)}"

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

    def _get_response_rest(self, url: str) -> list[dict[str, Any]]:
        """Make a GET request to the GitHub REST API.
        Handles pagination and rate limiting.

        Parameters
        ----------
        url : str
            The API endpoint URL.

        Returns
        -------
        list[dict[str, Any]]
            A list of JSON responses from GitHub API requests.
        """
        results = []
        api_endpoint_url = url

        try:
            while api_endpoint_url:
                response = requests.get(
                    api_endpoint_url,
                    headers={"Authorization": f"token {self.get_token()}"},
                )
                response.raise_for_status()
                results.extend(response.json())

                # Handle pagination & rate limiting
                api_endpoint_url = response.links.get("next", {}).get("url")
                self.handle_rate_limit(response)

        except requests.HTTPError as exception:
            if exception.response.status_code == 401:
                logger.error(
                    "Unauthorized request. Your token may be expired or invalid. Please refresh your token."
                )
            else:
                raise exception

        return results

    def get_gh_metrics(
        self,
        endpoints: dict[dict[str, str]],
        reviews: dict[str, ReviewModel],
    ) -> dict[str, ReviewModel]:
        """
        Get GitHub metrics for all reviews using provided repo name and owner.
        Does not work on GitLab currently

        Parameters:
        ----------
        endpoints : dict
            A dictionary mapping package names to their owner and repo-names.
        reviews : dict
            A dictionary containing review data.

        Returns:
        -------
        dict
            Updated review data with GitHub metrics.
        """

        for pkg_name, owner_repo in endpoints.items():
            reviews[pkg_name].gh_meta = self.get_repo_meta(owner_repo)

        return reviews

    def _get_contrib_count_rest(self, url: str) -> int | None:
        """
        Returns the count of total contributors to a repository.

        Uses the rest API because graphql can't access this specific metric

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
        # https://api.github.com/repos/{owner}/{repo}/contributors
        repo_contribs_url = f"https://api.github.com/repos/{url['owner']}/{url['repo_name']}/contributors"
        contributors = self._get_response_rest(repo_contribs_url)

        if not contributors:
            logger.warning(
                f"Repository not found: {repo_contribs_url}. Did the repo URL change?"
            )
            return None

        return len(contributors)

    def _get_metrics_graphql(
        self, repo_info: dict[str, str]
    ) -> dict[str, Any] | None:
        """
        Get GitHub metrics from the GitHub GraphQL API for a single repository.

        Parameters
        ----------
        repo_info : dict
            A dictionary containing the owner and repository name.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the specified GitHub metrics for the repository.
            Returns None if the repository is not found or access is forbidden.

        Notes
        -----
        This method makes a GraphQL call to the GitHub API to retrieve metadata
        about a pyos reviewed package repository.

        If the repository is not found or access is forbidden, this method returns None.
        """

        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                name
                description
                homepageUrl
                createdAt
                stargazers {
                    totalCount
                }
                watchers {
                    totalCount
                }
                issues(states: OPEN) {
                    totalCount
                }
                forks {
                    totalCount
                }
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history(first: 1) {
                                edges {
                                    node {
                                        committedDate
                                    }
                                }
                            }
                        }
                    }
                }
                collaborators {
                    totalCount
                }
            }
        }
        """

        variables = {
            "owner": repo_info["owner"],
            "name": repo_info["repo_name"],
        }

        headers = {"Authorization": f"Bearer {self.get_token()}"}

        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        if response.status_code == 200:
            data = response.json()
            repo_data = data["data"]["repository"]

            if not repo_data:
                logger.warning(
                    f"Repository metrics not able to be retrieved (it may not be on GitHub?): {repo_info['owner']}/{repo_info['repo_name']}."
                )
                return None

            return {
                "name": repo_data["name"],
                "description": repo_data["description"],
                "documentation": repo_data["homepageUrl"],
                "created_at": repo_data["createdAt"],
                "stargazers_count": repo_data["stargazers"]["totalCount"],
                "watchers_count": repo_data["watchers"]["totalCount"],
                "open_issues_count": repo_data["issues"]["totalCount"],
                "forks_count": repo_data["forks"]["totalCount"],
                "last_commit": repo_data["defaultBranchRef"]["target"][
                    "history"
                ]["edges"][0]["node"]["committedDate"],
            }
        elif response.status_code == 404:
            logger.warning(
                f"Repository not found: {repo_info['owner']}/{repo_info['repo_name']}. Did the repo URL change?"
            )
            return None
        elif response.status_code == 403:
            logger.warning(
                f"Oops! You may have hit an API limit for repository: {repo_info['owner']}/{repo_info['repo_name']}.\n"
                f"API Response Text: {response.text}\n"
                f"API Response Headers: {response.headers}"
            )
            return None
        else:
            logger.warning(
                f"Unexpected HTTP error: {response.status_code} for repository: {repo_info['owner']}/{repo_info['repo_name']}"
            )
            return None

    def get_repo_meta(
        self, repo_info: dict[str, str]
    ) -> dict[str, Any] | None:
        """Get GitHub metrics from the GitHub GraphQL API for a repository.

        Parameters
        ----------
        repo_info : dict
            A dictionary containing the owner and repository name.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the specified GitHub metrics for the repository.
            Returns None if the repository is not found or access is forbidden.

        Notes
        -----
        This method makes a GraphQL call to the GitHub API to retrieve metadata
        about a pyos reviewed package repository.

        If the repository is not found or access is forbidden, it returns None.
        """
        metrics = self._get_metrics_graphql(repo_info)
        if metrics is not None:
            metrics["contrib_count"] = self._get_contrib_count_rest(repo_info)

        return metrics

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
