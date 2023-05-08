"""
Script that parses metadata from na issue and adds it to a yml file for the
website. It also grabs some of the package metadata such as stars,
last commit, etc.

Output: packages.yml

To run: python3 parse_issue_metadata.py

# TODO: add maintainer list to the metadata!
"""


from pyosmeta import ProcessIssues
from pyosmeta.file_io import get_api_token

API_TOKEN = get_api_token()

# TODO: looks like sometimes the gh username is the name then @. so i need to create
# code that looks for the @ and adds the username to ghusername and the rest to the name
# result.status_code in [200, 302]:
# TODO: I get key errors and name errors when i hit api limits
# Would be good to track API return responses / figure out how long I need to wait
# so it doesn't just fail. how does that get setup?
issueProcess = ProcessIssues(
    org="pyopensci",
    repo_name="software-submission",
    label_name="6/pyOS-approved 🚀🚀🚀",
    API_TOKEN=API_TOKEN,
)

# Get all issues for approved packages
issues = issueProcess.return_response()
# breakpoint()
# Fixed:
review = issueProcess.parse_issue_header(issues, 12)

# Get list of GitHub API endpoint for each accepted package
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
    all_repo_meta[package_name] = issueProcess.get_repo_meta(package_api, gh_stats)

    all_repo_meta[package_name]["contrib_count"] = issueProcess.get_repo_contribs(
        package_api
    )
    all_repo_meta[package_name]["last_commit"] = issueProcess.get_last_commit(
        package_api
    )
    # Add github meta to review metadata
    review[package_name]["gh_meta"] = all_repo_meta[package_name]

# Turn the data into a list to support jekyll friendly yaml
final_data = []
for key in review:
    final_data.append(review[key])

final_yaml = "packages.yml"
# Export to yaml!
issueProcess.export_yaml(final_yaml, final_data)
issueProcess.clean_yaml_file(final_yaml)
