"""
A module that contains all of the methods related to interfacing
with the GitHub API. There are four groupings of activities:

1. Parsing GitHub issues to return pyOS software peer review information
2. Parsing contributor profile data to return names and affiliations where
available
3. Parsing package repositories to return package metadata such as pull request
numbers, stars and more "health & stability" related metrics
4. Fetching GitHub organization team members (editorial board and related
teams)
"""

import os
import time
from dataclasses import dataclass
from typing import Any, Optional, Union

import requests
from dotenv import load_dotenv
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from pyosmeta.models import ReviewModel
from pyosmeta.models.base import GhMeta, RepositoryHost

from .logging import logger


class GitHubAPIError(Exception):
    """Raised for GitHub API errors that affect the whole metrics run.

    Covers an invalid/expired token (401) and a fully exhausted rate limit
    (403 with ``X-RateLimit-Remaining: 0``).
    """


@dataclass
class GitHubAPI:
    """
    A class that processes GitHub issues in our peer review process and returns
    metadata about each package.

    This class contains variable that maps the GhMeta fields to the GitHub REST
    API fields. It also defines the source of the data for each field.
    """

    # `contrib_count` is populated separately from the contributors REST endpoint.
    GH_META_REQUIRED_FIELDS = tuple(GhMeta.model_fields.keys())
    GH_META_REST_FIELD_MAP = {
        "name": "name",
        "description": "description",
        "documentation": "homepage",
        "created_at": "created_at",
        "stargazers_count": "stargazers_count",
        "watchers_count": "watchers_count",
        "open_issues_count": "open_issues_count",
        "forks_count": "forks_count",
        "last_commit": "pushed_at",
    }
    GH_META_CONTRIB_SOURCE = "GET /repos/{owner}/{repo}/contributors"
    GH_META_LAST_COMMIT_SOURCE = GH_META_REST_FIELD_MAP["last_commit"]

    @classmethod
    def get_gh_meta_field_mapping(cls) -> dict[str, Any]:
        """Return the GhMeta field map and source details.

        Returns
        -------
        dict[str, Any]
            Mapping details describing required output fields and where each
            field comes from in the REST API payload or endpoint.
        """
        return {
            "required_fields": cls.GH_META_REQUIRED_FIELDS,
            "rest_field_map": cls.GH_META_REST_FIELD_MAP,
            "contrib_source": cls.GH_META_CONTRIB_SOURCE,
            "last_commit_source": cls.GH_META_LAST_COMMIT_SOURCE,
        }

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

        Used for issues, contributors, and package metrics. Org team reads
        use ``get_teams_token`` / ``GITHUB_TOKEN_TEAMS`` instead.

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

    def get_teams_token(self) -> str:
        """Return the token used to read GitHub organization teams.

        Reads ``GITHUB_TOKEN_TEAMS`` from the environment (or ``.env``).
        Team membership endpoints need org/team read permission that a
        public-repo PAT often does not have.

        Returns
        -------
        str
            The teams API token.

        Raises
        ------
        KeyError
            If ``GITHUB_TOKEN_TEAMS`` is not set.
        """
        load_dotenv()
        try:
            return os.environ["GITHUB_TOKEN_TEAMS"]
        except KeyError:
            raise KeyError(
                "Oops! A GITHUB_TOKEN_TEAMS environment variable wasn't "
                "found. Set it to a token that can read pyOpenSci org teams."
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

    @staticmethod
    def _is_rate_limit_exhausted(response) -> bool:
        """Return True if rate limit has been reached.

        The header is checked for `X-RateLimit-Remaining` to indicate if the
        primary rate limit is
        fully used up, as opposed to a plain permission-denied 403."""
        return response.headers.get("X-RateLimit-Remaining") == "0"

    @staticmethod
    def _format_rate_limit_reset(response) -> str:
        """Format the X-RateLimit-Reset header timestamp to a
        human-readable UTC time."""
        reset_header = response.headers.get("X-RateLimit-Reset")
        if not reset_header:
            return "unknown"
        try:
            return time.strftime(
                "%Y-%m-%d %H:%M:%S UTC", time.gmtime(int(reset_header))
            )
        except (TypeError, ValueError):
            return "unknown"

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

    def _get_response_rest(
        self,
        url: str,
        *,
        token: str | None = None,
        token_name: str = "GITHUB_TOKEN",
    ) -> list[dict[str, Any]]:
        """Make a GET request to the GitHub REST API.
        Handles pagination and rate limiting.

        Parameters
        ----------
        url : str
            The API endpoint URL.
        token : str, optional
            Auth token to use. Defaults to ``get_token()``
            (``GITHUB_TOKEN``).
        token_name : str, optional
            Env var name for 401 error messages.

        Returns
        -------
        list[dict[str, Any]]
            A list of JSON responses from GitHub API requests.
        """
        results = []
        api_endpoint_url = url
        auth_token = token if token is not None else self.get_token()

        while api_endpoint_url:
            response = requests.get(
                api_endpoint_url,
                headers={"Authorization": f"token {auth_token}"},
            )

            if response.status_code == 401:
                raise GitHubAPIError(
                    f"401 Unauthorized calling {api_endpoint_url}. Check "
                    f"that {token_name} is valid, unexpired, and has the "
                    "correct scopes."
                )
            if response.status_code == 403:
                if self._is_rate_limit_exhausted(response):
                    raise GitHubAPIError(
                        f"403 rate limit exhausted calling "
                        f"{api_endpoint_url}. Resets at "
                        f"{self._format_rate_limit_reset(response)}."
                    )
                logger.warning(
                    "403 Forbidden (permission denied, not rate-limited) "
                    f"calling {api_endpoint_url}.\n"
                    f"API Response Text: {response.text}"
                )
                break

            response.raise_for_status()
            results.extend(response.json())

            # Handle pagination & rate limiting
            api_endpoint_url = response.links.get("next", {}).get("url")
            self.handle_rate_limit(response)

        return results

    def get_metrics(
        self,
        endpoints: dict[str, dict[str, str]],
        reviews: dict[str, ReviewModel],
    ) -> dict[str, ReviewModel]:
        """
        Fetch GitHub metrics for all reviews using provided repo name and owner.
        Does not work on GitLab currently.

        On success, sets ``review.gh_meta`` from the API response (date fields
        are cleaned via the ``GhMeta`` model). On failure, leaves ``gh_meta``
        as ``None`` so a separate merge step can gap-fill from previously
        published packages.yml data.

        If a ``GitHubAPIError`` is raised (401 or exhausted rate-limit 403),
        further API fetches for remaining packages are stopped
        (``stop_metrics_run``). Those packages keep ``gh_meta=None`` for the
        merge step to fill.

        Parameters:
        ----------
        endpoints : dict
            A dictionary mapping package names to their owner and repo-names.
        reviews : dict
            A dictionary containing review data.

        Returns:
        -------
        dict
            Review data with freshly fetched ``gh_meta`` where the API
            succeeded, or ``None`` where it did not.
        """
        # If True, metrics run should stop further API fetches
        stop_metrics_run = False

        for pkg_name, owner_repo in tqdm(
            endpoints.items(), desc="Fetching repo metadata"
        ):
            with logging_redirect_tqdm():
                review = reviews[pkg_name]
                if review.repository_host != RepositoryHost.github:
                    logger.warning(
                        f"Unsupported repository host for {pkg_name}: "
                        f"{review.repository_host}"
                    )
                    continue

                new_metadata = None
                if not stop_metrics_run:
                    try:
                        new_metadata = self.get_repo_meta_github(owner_repo)
                    except GitHubAPIError as exc:
                        logger.error(
                            f"Stopping GitHub metrics run early: {exc} "
                            "Remaining packages will keep empty gh_meta for "
                            "gap-fill from previously saved metrics."
                        )
                        stop_metrics_run = True
                    except Exception:
                        logger.warning(
                            f"Unexpected error fetching GitHub metrics for "
                            f"{pkg_name}. Treating this package as a failed "
                            "fetch.",
                            exc_info=True,
                        )
                        new_metadata = None

                if new_metadata is not None:
                    reviews[pkg_name].gh_meta = new_metadata

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

    def _get_metrics_rest(
        self, repo_info: dict[str, str]
    ) -> dict[str, Any] | None:
        """Get GitHub metadata from the GitHub REST API for a single repository.

        Parameters
        ----------
        repo_info : dict
            A dictionary containing the owner and repository name.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing GhMeta-compatible metadata for the
            repository, normalized using GH_META_REST_FIELD_MAP.
            Returns None if the repository is not found or access is
            forbidden.

        Notes
        -----
        This method calls GET /repos/{owner}/{repo} to retrieve metadata
        about a pyos reviewed package repository. `contrib_count` is not
        included here - it's fetched separately via _get_contrib_count_rest.

        If the repository is not found or access is forbidden, this method
        returns None.
        """
        owner = repo_info["owner"]
        repo_name = repo_info["repo_name"]
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {"Authorization": f"Bearer {self.get_token()}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repo_data = response.json()
            metrics = {
                gh_meta_field: repo_data.get(rest_field)
                for gh_meta_field, rest_field in self.GH_META_REST_FIELD_MAP.items()
            }
            # GitHub returns an empty string (not null) when no homepage
            # is set, so normalize that to None for GhMeta.
            if not metrics.get("documentation"):
                metrics["documentation"] = None
            return metrics
        elif response.status_code == 404:
            logger.warning(
                f"Repository not found: {owner}/{repo_name}. Did the repo URL change?"
            )
            return None
        elif response.status_code == 401:
            raise GitHubAPIError(
                f"401 Unauthorized calling {url}. Check that GITHUB_TOKEN "
                "is valid, unexpired, and has the correct scopes."
            )
        elif response.status_code == 403:
            if self._is_rate_limit_exhausted(response):
                raise GitHubAPIError(
                    f"403 rate limit exhausted calling {url}. Resets at "
                    f"{self._format_rate_limit_reset(response)}."
                )
            logger.warning(
                "403 Forbidden (permission denied, not rate-limited) for "
                f"repository: {owner}/{repo_name}.\n"
                f"API Response Text: {response.text}"
            )
            return None
        else:
            logger.warning(
                f"Unexpected HTTP error: {response.status_code} for repository: {owner}/{repo_name}"
            )
            return None

    def get_repo_meta_github(
        self, repo_info: dict[str, str]
    ) -> dict[str, Any] | None:
        """Get GitHub metadata for a repository, REST-first.

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
        REST (`_get_metrics_rest`) is the primary and only source used here
        for repository metadata, so this works with a general token without
        requiring org membership or elevated permissions. Contributor count
        is fetched separately via `_get_contrib_count_rest`, since it isn't
        part of the main repo metadata endpoint.

        If the repository is not found or access is forbidden, it returns None.
        """
        metrics = self._get_metrics_rest(repo_info)
        if metrics is not None:
            metrics["contrib_count"] = self._get_contrib_count_rest(repo_info)

        return metrics

    def get_repo_meta_gitlab(
        self, repo_info: dict[str, str]
    ) -> dict[str, Any] | None:
        raise NotImplementedError

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

    def get_team_members(self, slug: str) -> list[str]:
        """Return GitHub logins for members of an organization team.

        Uses the REST API (``GET /orgs/{org}/teams/{slug}/members``) and
        follows pagination via ``_get_response_rest``. Team membership is
        the source of truth for pyOpenSci editor listings.

        Parameters
        ----------
        slug : str
            GitHub team slug, e.g. ``editorial-board`` or ``eic-team``.

        Returns
        -------
        list[str]
            GitHub usernames for the team's members.

        Raises
        ------
        GitHubAPIError
            If the token is invalid (401) or rate-limited (403).
        requests.HTTPError
            If the team is missing or inaccessible (GitHub answers 404
            when the token cannot read a private team). Reading org teams
            needs ``GITHUB_TOKEN_TEAMS`` with team read permission.
        """
        if not self.org:
            raise GitHubAPIError(
                "An organization name is required to fetch team members."
            )

        url = (
            f"https://api.github.com/orgs/{self.org}/teams/{slug}"
            "/members?per_page=100"
        )
        members = self._get_response_rest(
            url,
            token=self.get_teams_token(),
            token_name="GITHUB_TOKEN_TEAMS",
        )

        logins: list[str] = []
        for member in members:
            if not member:
                continue
            login = (member.get("login") or "").strip()
            if login:
                logins.append(login)

        return logins
