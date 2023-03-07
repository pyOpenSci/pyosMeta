from dataclasses import dataclass
from datetime import datetime

import requests
import ruamel.yaml


@dataclass
class ProcessIssues:
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
    def _get_response(self, username):
        """
        # Make a GET request to the API endpoint
        """
        try:
            print(self.api_endpoint)
            return requests.get(self.api_endpoint, auth=(username, self.API_TOKEN))
        except:
            print(f"Error: API request failed with status code {response.status_code}")

    def return_response(self, username):
        """
        returns the response in a deserialize json to dict
        """
        response = self._get_response(username)
        return response.json()

    def _contains_keyword(self, string: str) -> bool:
        """
        Returns true if starts with any of the 3 items below.
        """
        return string.startswith(("Submitting", "Editor", "Reviewer"))

    def get_issue_meta(self, line_item: list) -> dict:
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
        if self._contains_keyword(item[0]):
            names = line_item[1].split("(", 1)
            if len(names) > 1:
                meta[line_item[0]] = {
                    "name": names[0].strip(),
                    "github_username": names[1].strip().lstrip("@").rstrip(")"),
                }
            else:
                meta[line_item[0]] = {
                    "name": "",
                    "github_username": names[0].strip().lstrip("@"),
                }
        else:
            if len(item) > 1:
                meta[line_item[0]] = item[1]

        return meta

    # review_issues = review
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
            print(aPackage)
            repo = review[aPackage]["Repository Link"]
            print(repo)
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
        package_name = body_data[1][1]
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
        response = requests.get(url)

        if response.status_code == 404:
            print("Can't find: ", url, ". Did the repo url change?")
        # Extract the description and homepage URL from the response JSON
        else:
            data = response.json()
            for astat in stats_list:
                print(astat)
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
        response = requests.get(repo_contribs)

        if response.status_code == 404:
            print("Can't find: ", url, ". Did the repo url change?")
        # Extract the description and homepage URL from the response JSON
        else:
            return len(response.json())

    def get_last_commit(self, repo: str) -> str:
        """ """
        url = repo + "/commits"
        response = requests.get(url).json()
        date = response[0]["commit"]["author"]["date"]

        return self._clean_date(date)

    def get_categories(self, issue_body_list: list) -> list:
        """Parse through a pyos issue and grab the categories associated
        with a package

        Parameters
        ----------
        issue_body_list : list
            List containing each line in the first comment of the issue
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
        categories = []
        for i in range(start_index + 1, len(issue_body_list)):
            line = issue_body_list[i][0]
            if line.startswith("\t-") and "[x]" in line:
                category = line[line.index("]") + 2 :]
                categories.append(category)

        return categories


# TODO: Several packages are returning empty categories after parsing the issue- pyrolite,MovingPandas, pandera:
# TODO: add date issue closed as well - can get that from API maybe?

issueProcess = ProcessIssues(
    org="pyopensci",
    repo_name="software-submission",
    label_name="6/pyOS-approved 🚀🚀🚀",
    API_TOKEN=API_TOKEN,
)

# Get all issues for approved packages
issues = issueProcess.return_response("lwasser")

# Loop through each issue and print the text in the first comment
review = {}
for issue in issues:
    package_name, body_data = issueProcess.parse_comment(issue)
    # review_meta = {}
    # index of 12 should include date accepted
    issue_meta = {}
    for item in body_data[0:12]:
        # TODO - add date accepted if it exists
        issue_meta.update(issueProcess.get_issue_meta(item))

    review[package_name] = issue_meta
    review[package_name]["categories"] = issueProcess.get_categories(body_data)

# Get list of github API endpoint for each accepted package
all_repo_endpoints = issueProcess.get_repo_endpoints(review)

# Send a GET request to the API endpoint and include a user agent header
gh_stats = [
    "name",
    "description",
    "homepage",
    "created_at",
    "stargazers_count",
    "watchers_count",
    "stargazers_count",
    "forks",
    "open_issues_count",
    "forks_count",
]


# Get gh metadata for each package submission
all_repo_meta = {}
for package_name in all_repo_endpoints.keys():
    print(package_name)
    package_api = all_repo_endpoints[package_name]
    print(package_api)
    all_repo_meta[package_name] = issueProcess.get_repo_meta(package_api, gh_stats)

    all_repo_meta[package_name]["contrib_count"] = issueProcess.get_repo_contribs(
        package_api
    )
    all_repo_meta[package_name]["last_commit"] = issueProcess.get_last_commit(
        package_api
    )
    # Add github meta to review metadata
    review[package_name]["gh_meta"] = all_repo_meta[package_name]


filename = "packages.yml"
with open(filename, "w") as file:
    # Create YAML object with RoundTripDumper to keep key order intact
    yaml = ruamel.yaml.YAML(typ="rt")
    # Set the indent parameter to 2 for the yaml output
    yaml.indent(mapping=4, sequence=4, offset=2)
    yaml.dump(review, file)

# https://api.github.com/repos/pyopensci/python-package-guide/commits
