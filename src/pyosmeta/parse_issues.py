import re
import warnings

import requests
from dataclasses import dataclass
from typing import Any

from .contributors import ProcessContributors
from .utils_clean import clean_date_accepted_key, clean_markdown
from .utils_parse import parse_user_names


@dataclass
class ProcessIssues:
    """
    A class that processes GitHub issues in our peer review process and returns
    metadata about each package.
    """

    def __init__(self, org: str, repo_name: str, label_name: str):
        """
        More here...

        Parameters
        ----------
        org : str
            Organization name where the issues exist
        repo_name : str
            Repo name where the software review issues live
        label_name : str
            Label of issues to grab - e.g. pyos approved
        GITHUB_TOKEN : str
            API token needed to authenticate with GitHub
            Inherited from super() class
        """
        self.org: str = org
        self.repo_name: str = repo_name
        self.label_name: str = label_name
        self.contrib_instance = ProcessContributors([])

        self.GITHUB_TOKEN = self.contrib_instance.get_token()

    gh_stats = [
        "name",
        "description",
        "homepage",
        "created_at",
        "stargazers_count",
        "watchers_count",
        "open_issues_count",
        "forks_count",
    ]

    @property
    def api_endpoint(self):
        url = (
            f"https://api.github.com/repos/{self.org}/{self.repo_name}/"
            f"issues?labels={self.label_name}&state=all&per_page=100"
        )
        return url

    # Set up the API endpoint
    def _get_response(self):
        """
        # Make a GET request to the API endpoint
        """

        print(self.api_endpoint)

        try:
            response = requests.get(
                self.api_endpoint,
                headers={"Authorization": f"token {self.GITHUB_TOKEN}"},
            )
            response.raise_for_status()

        except requests.HTTPError as exception:
            raise exception

        return response

    def return_response(self) -> list[dict[str, object]]:
        """
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
        response = self._get_response()
        return response.json()

    def _is_review_role(self, string: str) -> bool:
        """
        Returns true if starts with any of the 3 items below.
        """
        return string.startswith(
            ("Submitting", "Editor", "Reviewer", "All current maintainers")
        )

    def _remove_extra_chars(self, a_str: str) -> str:
        """Helper to strip unwanted characters from text"""

        unwanted = ["(", ")", "@"]
        for char in unwanted:
            a_str = a_str.replace(char, "")

        return a_str.strip()

    def parse_issue_header(
        self, issues: list[str], total_lines: int = 20
    ) -> dict[str, str]:
        """Parses through each header comment for selected reviews and returns
        review metadata.

        Returns:
        GitHub Issue meta: "created_at", "updated_at", "closed_at"

        Parameters
        ----------
        issues : list
            List returned from the return_response method that contains the
            metadata at the top of each issue
        total_lines : int
            an integer representing the total number of lines to parse in the
            issue header. Default = 20

        Returns
        -------
        Dict
            A dictionary containing metadata for the issue including the
            package name, description, review team, version submitted etc.
            See key_order below for the full list of keys.
        """

        meta_dates = ["created_at", "updated_at", "closed_at"]

        review = {}
        review_final = {}
        for issue in issues:
            # Return issue comment as cleaned list + package name
            pkg_name, body_data = self.comment_to_list(issue)
            if pkg_name.lower() == "pynteny":
                print("halt")
            if not pkg_name:
                continue

            review[pkg_name] = self.get_issue_meta(body_data, total_lines)

            # Normalize date accepted key to be the same in each review
            review[pkg_name] = clean_date_accepted_key(review[pkg_name])

            # Add issue open and close date to package meta from GH response
            # Date cleaning happens via pydantic validator not here
            for a_date in meta_dates:
                review[pkg_name][a_date] = issue[a_date]

            review[pkg_name]["issue_link"] = issue["url"].replace(
                "https://api.github.com/repos/", "https://github.com/"
            )

            # Get categories and issue review link
            review[pkg_name]["categories"] = self.get_categories(
                body_data, "## Scope", 10
            )
            # NOTE: right now the numeric value is hard coded based on the
            # number of categories listed in the issue template.
            # this could be made more flexible if it just runs until it runs
            # out of categories to parse
            review[pkg_name]["partners"] = self.get_categories(
                body_data, "## Community Partnerships", 3
            )
            # TODO: the current workflow will not parse domains
            # add a separate workflow to parse domains and add them to the
            # categories list
            # review[pkg_name]["domains"] = self.get_categories(body_data,
            #                                                    '## Domains',
            #                                                    3)

            # Only return keys for metadata that we need
            final_keys = [
                "submitting_author",
                "all_current_maintainers",
                "package_name",
                "one-line_description_of_package",
                "repository_link",
                "version_submitted",
                "editor",
                "reviewer_1",
                "reviewer_2",
                "archive",
                "version_accepted",
                "joss_doi",
                "date_accepted",
                "categories",
                "partners",
                "domain",
                "created_at",
                "updated_at",
                "closed_at",
                "issue_link",
                "categories",
            ]

            review_final[pkg_name] = {
                key: review[pkg_name][key]
                for key in final_keys
                if key in review[pkg_name].keys()
            }

        return review_final

    def get_contributor_data(self, line: list[str]) -> dict[str, str | int]:
        """Parse names for various review roles from issue metadata.

        Parameters
        ----------
        line : list of str
            A single list item representing a single line in the issue
            containing metadata for the review.

        Returns
        -------
        dict
            Containing the metadata for a submitting author, reviewer, or
            maintainer(s).
        """

        meta = {}
        a_key = line[0].lower().replace(" ", "_")

        if line[0].startswith("All current maintainers"):
            names = line[1].split(",")
            meta[a_key] = []
            for name in names:
                # Add each maintainer to the dict
                a_maint = parse_user_names(username=name)
                meta[a_key].append(a_maint)
        else:
            names = parse_user_names(line[1])
            meta[a_key] = names

        return meta

    def get_issue_meta(
        self,
        body_data: list[str],
        end_range: int,
    ) -> dict[str, str]:
        """Process a single review returning metadata for that review.

        Parse through a list of strings, each of which represents a line in the
        first comment of a review. Return the cleaned review metadata.

        Parameters
        ----------
        body_data : list
            A list containing all body data for the top comment in an issue.
        end_range : int
            The number of lines to parse at the top of the issue (this may
            change over time so this variable allows us to have different
            processing based upon the date of the issue being opened)

        Returns
        -------
            dict
        """
        issue_meta = {}
        # TODO: change to for line in review_comment
        for single_line in body_data[0:end_range]:
            meta = {}
            a_key = single_line[0].lower().replace(" ", "_")
            # If the line is for a review role - editor, maintainer, reviewer
            if self._is_review_role(single_line[0]):
                # Collect metadata for each review role
                meta = self.get_contributor_data(single_line)
            elif len(single_line) > 1:
                meta[a_key] = single_line[1].strip()
            else:
                meta[a_key] = self._remove_extra_chars(single_line[0])

            issue_meta.update(meta)

        return issue_meta

    def get_repo_endpoints(
        self, review_issues: dict[str, str]
    ) -> dict[str, str]:
        """
        Returns a list of repository endpoints

        Parameters
        ----------
        review_issues : dict
            Dictionary containing all of the review issue paths.

        Returns
        -------
            Dict
                Containing pkg_name: endpoint for each review.

        """

        all_repos = {}
        for a_package in review_issues.keys():
            repo = review_issues[a_package]["repository_link"].strip("/")
            owner, repo = repo.split("/")[-2:]
            # TODO: could be simpler code - Remove any link remnants
            pattern = r"[\(\)\[\]?]"
            owner = re.sub(pattern, "", owner)
            repo = re.sub(pattern, "", repo)
            all_repos[a_package] = (
                f"https://api.github.com/repos/{owner}/{repo}"
            )
        return all_repos

    def comment_to_list(self, issue: dict[str, str]) -> tuple[str, list[str]]:
        """Parses the first comment in a pyOpenSci review issue.

        Returns the package name
        and the body of the comment parsed into a list of elements.

        Parameters
        ----------
        issue : dict
            A dictionary containing the json response for an issue comment.

        Returns
        -------
            pkg_name : str
                The name of the package
            comment : list
                A list containing the comment elements in order
        """

        body = issue["body"]
        # Clean line breaks (could be done with a regex too)
        lines = body.split("\n")
        lines = [a_line.strip("\r").strip() for a_line in lines]
        # Some users decide to hold the issue titles.
        # For those, clean the markdown bold ** element
        lines = [
            line.replace("**", "").strip()
            for line in lines
            if line.strip() != ""
        ]
        # You need a space after : or else it will break https:// in two
        body_data = [line.split(": ") for line in lines if line.strip() != ""]

        # Loop through issue header and grab relevant review metadata
        name_index = next(
            (
                i
                for i, sublist in enumerate(body_data)
                if sublist[0] == "Package Name"
            ),
            None,
        )

        if name_index is None:
            warnings.warn(
                "Package Name not found in the issue comment.", UserWarning
            )
            pkg_name = "missing_name"
        else:
            pkg_name = body_data[name_index][1]

        return clean_markdown(pkg_name), body_data

    def get_gh_metrics(
        self,
        endpoints: dict[str, str],
        reviews: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """
        Get GitHub metrics for each review based on provided endpoints.

        Parameters:
        ----------
        endpoints : dict
            A dictionary mapping package names to their GitHub URLs.
        reviews : dict
            A dictionary containing review data.

        Returns:
        -------
        dict
            Updated review data with GitHub metrics.
        """
        pkg_meta = {}
        for pkg_name, url in endpoints.items():
            pkg_meta[pkg_name] = self.get_repo_meta(url, self.gh_stats)

            pkg_meta[pkg_name]["contrib_count"] = self.get_repo_contribs(url)
            pkg_meta[pkg_name]["last_commit"] = self.get_last_commit(url)
            # Add github meta to review metadata
            reviews[pkg_name]["gh_meta"] = pkg_meta[pkg_name]

        return reviews

    def get_repo_meta(self, url: str, stats_list: list) -> dict:
        """
        Returns a set of GH stats from each repo of our reviewed packages.

        """
        stats_dict = {}
        # Get the url (normally the docs) and description of a repo!
        response = requests.get(
            url, headers={"Authorization": f"token {self.GITHUB_TOKEN}"}
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

        # Extract the description and homepage URL from the response JSON
        else:
            data = response.json()
            for astat in stats_list:
                stats_dict[astat] = data[astat]
            stats_dict["documentation"] = stats_dict.pop("homepage")

        return stats_dict

    def get_repo_contribs(self, url: str) -> dict:
        """
        Returns a list of contributors to a specific repo.

        """
        repo_contribs = url + "/contributors"
        # Small script to get the url (normally the docs) and repo description
        response = requests.get(
            repo_contribs,
            headers={"Authorization": f"token {self.GITHUB_TOKEN}"},
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
            url, headers={"Authorization": f"token {self.GITHUB_TOKEN}"}
        ).json()
        date = response[0]["commit"]["author"]["date"]

        return date

    # This works - i could just make it more generic and remove fmt since it's
    # not used and replace it with a number of values and a test string
    def get_categories(
        self, issue_list: list[list[str]], section_str: str, num_vals: int
    ) -> list[str]:
        """Parse through a pyOS review issue and grab categories associated
        with a package

        Parameters
        ----------
        issue_list : list[list[str]]
            The first comment from the issue split into lines and then the
            lines split as by self.comment_to_list()

        section_str : str
            The section string to find where the categories live in the review
            metadata. Example ## Scope contains the package categories such as
            data viz, etc

        num_vals : int
            Number of categories expected in the list. for instance
            3 partner options.
        """
        # Find the starting index of the category section
        # This will be more robust if we use starts_with rather than in i think
        try:
            index = next(
                i
                for i, sublist in enumerate(issue_list)
                if section_str in sublist
            )
            # Iterate starting at the specified section location index
            # find the first line starting with " - ["
            # This represents the first category in a list of categories
            for i in range(index + 1, len(issue_list)):
                if issue_list[i] and issue_list[i][0].startswith("- ["):
                    cat_index = i
                    break
        except StopIteration:
            print(section_str, "not found in the list.")
            return None

        # Get checked categories for package
        # TODO: it would be nice to figure out where the end of the list is
        # rather than hard coding it
        cat_list = issue_list[cat_index : cat_index + num_vals]
        selected = [
            item[0] for item in cat_list if re.search(r"- \[[xX]\] ", item[0])
        ]
        # Above returns a list of list elements that are checked
        # Now, clean the extra markdown and only return the category text
        cleaned = [re.sub(r"- \[[xX]\] ", "", item) for item in selected]
        categories = [
            re.sub(r"(\w+) (\w+)", r"\1-\2", item) for item in cleaned
        ]
        return [item.lower().replace("[^1]", "") for item in categories]
