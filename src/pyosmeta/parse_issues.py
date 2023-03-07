from dataclasses import dataclass
from datetime import datetime

import requests
import ruamel.yaml


@dataclass
class ProcessIssues:
    # When initializing how do you decide what should be an input
    # attribute vs just something a method accepted when called?
    """
    Parameters
    ----------
    org : str
    repo_name : str
    tag_name : str
    API_TOKEN : str
    username : str
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

    def get_issue_meta(self, issue_header: list):
        """
        Parameters
        ----------
        issue_header : list
            A list of items that represent lines in the first comment of an issue
            This comment is the metadata for the review that the author fills out.
        """

        if self._contains_keyword(item[0]):
            names = item[1].split("(", 1)
            if len(names) > 1:
                review_meta[item[0]] = {
                    "name": names[0].strip(),
                    "github_username": names[1].strip().lstrip("@").rstrip(")"),
                }
            else:
                review_meta[item[0]] = {
                    "name": "",
                    "github_username": names[0].strip().lstrip("@"),
                }
        else:
            if len(item) > 1:
                review_meta[item[0]] = item[1]

        return review_meta

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
        last_commit = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()

        return last_commit.strftime("%m/%d/%Y")


issueProcess = ProcessIssues(
    org="pyopensci",
    repo_name="software-submission",
    label_name="6/pyOS-approved 🚀🚀🚀",
    API_TOKEN=API_TOKEN,
)

# Get API response
response = issueProcess.return_response("lwasser")

# TODO: could make this a method too?
# Loop through each issue and print the text in the first comment
review = {}
for issue in issues:
    package_name, body_data = issueProcess.parse_comment(issue)
    review_meta = {}
    for item in body_data[0:11]:
        review[package_name] = issueProcess.get_issue_meta(item)

# Get a list of github repos for reviews
# This now returns a dict...
all_repo_endpoints = issueProcess.get_repo_endpoints(review)
# above used to be all_repos

# TODO:
# Add date accepted to the issue
# add date issue closed as well - can get that from API maybe?


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

stats_list = gh_stats
url = "https://api.github.com/repos/earthlab/earthpy"

# meta = issueProcess.get_repo_meta(url, stats_list)

# Get gh metadata for each package submission
all_repo_meta = {}
for package_name in all_repos.keys():
    print(package_name)
    all_repo_meta[package_name] = issueProcess.get_repo_meta(repo, gh_stats)

    all_repo_meta[package_name]["contrib_count"] = issueProcess.get_repo_contribs(repo)
    all_repo_meta[package_name]["last_commit"] = issueProcess.get_last_commit(repo)
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


"""
Add: to data
  date-accepted: 2021-12-29
  highlight:
  docs-url: "https://jointly.readthedocs.io"
  citation-link:


# Create dict with info
# Using create contrib file method from other script

  - package-name: jointly
  description: "Jointly: A Python package for synchronizing multiple sensors with accelerometer data"
  maintainer:
    [
      "Arne Herdick",
      "Felix Musmann",
      "Ariane Sasso",
      "Justin Albert",
      "Bert Arnrich",
    ]
  link: "https://github.com/hpi-dhc/jointly"
  date-accepted: 2021-12-29
  highlight:
  docs-url: "https://jointly.readthedocs.io"
  citation-link: "https://doi.org/10.5281/zenodo.5833858"
"""
