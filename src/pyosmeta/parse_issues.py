from dataclasses import dataclass
from datetime import datetime

import requests

from .file_io import YamlIO


# main reason to use this is attributes .. avoiding them being changed
# in other instances...
@dataclass
class ProcessIssues(YamlIO):
    """
    A class that processes GitHub issues in our peer review process and returns
    metadata about each package.

    Parameters
    ----------
    org : str
        Organization name where the issues exist
    repo_name : str
        Repo name where the software review issues live
    tag_name : str
        Tag of issues to grab - e.g. pyos approved
    API_TOKEN : str
        API token needed to authenticate with GitHub
    username : str
        Username needed to authenticate with GitHub
    """

    API_TOKEN: str = ""
    org: str = ""
    repo_name: str = ""
    label_name: str = ""
    username: str = ""

    @property
    def api_endpoint(self):
        return f"https://api.github.com/repos/{self.org}/{self.repo_name}/issues?labels={self.label_name}&state=all"

    # Set up the API endpoint
    # TODO: can i call the API endpoint above
    def _get_response(self):
        """
        # Make a GET request to the API endpoint
        """

        print(self.api_endpoint)

        try:
            response = requests.get(
                self.api_endpoint, headers={"Authorization": f"token {self.API_TOKEN}"}
            )
            response.raise_for_status()

        except requests.HTTPError as exception:
            raise exception

        return response

    def return_response(self) -> list:
        """
        Deserialize json response to dict and return.

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

    def _contains_keyword(self, string: str) -> bool:
        """
        Returns true if starts with any of the 3 items below.
        """
        return string.startswith(
            ("Submitting", "Editor", "Reviewer", "All current maintainers")
        )

    def _get_line_meta(self, line_item: list) -> dict:
        """
        Parameters
        ----------
        issue_header : list
            A single list item representing a single line in the issue
            containing metadata for the review.
            This comment is the metadata for the review that the author fills out.

        Returns
        -------
            Dict containing the metadata for a submitting author or reviewer
        """

        meta = {}
        theKey = line_item[0].lower().replace(" ", "_")
        if self._contains_keyword(line_item[0]):
            if line_item[0].startswith("All current maintainers"):
                names = line_item[1].split(", ")
                meta[theKey] = []
                for name in names:
                    meta[theKey].append(
                        {
                            "github_username": name.strip()
                            .lstrip("(")
                            .lstrip("@")
                            .rstrip(")"),
                            "name": "",
                        }
                    )
            else:
                names = line_item[1].split("(", 1)
                if len(names) > 1:
                    meta[theKey] = {
                        "github_username": names[1].strip().lstrip("@").rstrip(")"),
                        "name": names[0].strip(),
                    }
                else:
                    meta[theKey] = {
                        "github_username": names[0].strip().lstrip("@"),
                        "name": "",
                    }
        else:
            if len(line_item) > 1:
                meta[theKey] = line_item[1].strip()
        return meta

    def parse_issue_header(self, issues: list, total_lines: int = 15) -> dict:
        """
        Parameters
        ----------
        issues : list
            List returned from the return_response method that contains the
            metadata at the top of each issue
        total_lines : int
            an integer representing the total number of lines to parse in the
            issue header. Default = 15
        """
        # Reorder data
        key_order = [
            "package_name",
            "package_description",
            "submitting_author",
            "all_current_maintainers",
            "repository_link",
            "version_submitted",
            "categories",
            "editor",
            "reviewer_1",
            "reviewer_2",
            "archive",
            "version_accepted",
            "created_at",
            "updated_at",
            "closed_at",
        ]
        meta_dates = ["created_at", "updated_at", "closed_at"]

        review = {}
        for issue in issues:
            package_name, body_data = self.parse_comment(issue)
            # index of 15 should include date accepted
            issue_meta = self.get_issue_meta(body_data, total_lines)
            # Add issue open and close date to package meta
            for adate in meta_dates:
                issue_meta[adate] = issue[adate]
            review[package_name] = issue_meta
            review[package_name]["categories"] = self.get_categories(body_data)
            # Rename package description & reorder keys
            print(review[package_name].keys())
            review[package_name]["package_description"] = review[package_name].pop(
                "one-line_description_of_package"
            )
            review[package_name] = {
                key: review[package_name][key]
                for key in key_order
                if review[package_name].get(key)
            }
        return review

    def get_issue_meta(
        self,
        body_data: list,
        end_range: int,
    ) -> dict:
        """
        Parse through the top of an issue and grab the metadata for the review.

        Parameters
        ----------
        body_data : list
            A list containing all of the body data for the top comment in an issue.
        end_range : int
            The number of lines to parse at the top of the issue (this may change
            over time so this variable allows us to have different processing
            based upon the date of the issue being opened)

        """
        issue_meta = {}
        for item in body_data[0:end_range]:
            issue_meta.update(self._get_line_meta(item))
        # TODO Reorder keys so package_name is first, description then submitting
        return issue_meta

    def get_repo_endpoints(self, review_issues: dict):
        """
        Returns a list of repository endpoints

        Parameters
        ----------
        review_issue : dict

        Returns
        -------
            List of repository endpoints

        """

        all_repos = {}
        for aPackage in review_issues.keys():
            repo = review_issues[aPackage]["repository_link"]
            owner, repo = repo.split("/")[-2:]
            all_repos[aPackage] = f"https://api.github.com/repos/{owner}/{repo}"
        return all_repos

    def parse_comment(self, issue: dict):
        """
        Parses an issue comment for pyos review and returns the package name and
        the body of the comment parsed into a list of elements.

        Parameters
        ----------
        issue : dict
            A dictionary containing the json response for an issue comment.


        Returns
        -------
            package_name : str
                The name of the package
            comment : list
                A list containing the comment elements in order
        """

        comments_url = issue["comments_url"]
        body = issue["body"]

        lines = body.split("\r\n")
        body_data = [line.split(": ") for line in lines if line.strip() != ""]

        # Loop through issue header and grab relevant review metadata
        name_index = next(
            (i for i, sublist in enumerate(body_data) if sublist[0] == "Package Name"),
            None,
        )

        package_name = body_data[name_index][1]
        print(package_name)

        return package_name, body_data

    def _clean_date(self, date: str) -> str:
        """Cleans up a datetime  from github and returns a date string"""

        date_clean = (
            datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date().strftime("%m/%d/%Y")
        )
        return date_clean

    def get_repo_meta(self, url: str, stats_list: list) -> dict:
        """
        Returns a set of GH stats from each repo of our reviewed packages.

        """
        stats_dict = {}
        # Small script to get the url (normally the docs) and description of a repo!
        response = requests.get(
            url, headers={"Authorization": f"token {self.API_TOKEN}"}
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
            stats_dict["created_at"] = self._clean_date(stats_dict["created_at"])

        return stats_dict

    def get_repo_contribs(self, url: str) -> dict:
        """
        Returns a set of GH stats from each repo of our reviewed packages.

        """
        repo_contribs = url + "/contributors"
        # Small script to get the url (normally the docs) and description of a repo!
        response = requests.get(
            repo_contribs, headers={"Authorization": f"token {self.API_TOKEN}"}
        )

        if response.status_code == 404:
            print("Can't find: ", url, ". Did the repo url change?")
        # Extract the description and homepage URL from the response JSON
        else:
            return len(response.json())

    def get_last_commit(self, repo: str) -> str:
        """ """
        url = repo + "/commits"
        response = requests.get(
            url, headers={"Authorization": f"token {self.API_TOKEN}"}
        ).json()
        date = response[0]["commit"]["author"]["date"]

        return self._clean_date(date)

    def get_categories(
        self, issue_body_list: list[list[str]], fmt: bool = True
    ) -> list[str]:
        """Parse through a pyos issue and grab the categories associated
        with a package

        Parameters
        ----------
        issue_body_list : list[list[str]]
            The first comment from the issue split into lines and then the lines split as by self.parse_comment()

        fmt : bool
            Applies some formatting changes to the categories to match what is required for the website.
        """
        # Find the starting index of the section we're interested in
        start_index = None
        for i in range(len(issue_body_list)):
            if issue_body_list[i][0].startswith("- Please indicate which"):
                start_index = i
                break

        if start_index is None:
            # If we couldn't find the starting index, return an empty list
            return []

        # Iterate through the lines starting at the starting index and grab the relevant text
        cat_matches = ["[x]", "[X]"]
        categories: list[str] = []
        for i in range(start_index + 1, len(issue_body_list)):  # 30):
            line = issue_body_list[i][0].strip()
            checked = any([x in line for x in cat_matches])
            # TODO could i change the if to a while loop?
            if line.startswith("- [") and checked:
                category = line[line.index("]") + 2 :]
                categories.append(category)
            elif not line.startswith("- ["):
                break
            # elif line.strip().startswith("* Please fill out a pre-submission"):
            #     break

        if fmt:
            categories = [c.lower().replace(" ", "-") for c in categories]
        return categories


# https://api.github.com/repos/pyopensci/python-package-guide/commits
