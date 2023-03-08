import pickle

import ruamel.yaml

from pyosmeta.parse_issues import ProcessIssues

with open("../token.pickle", "rb") as f:
    API_TOKEN = pickle.load(f)


""" Begin processing issues """

# TODO - NameError: name 'ruamel' is not defined - it's part of the package tho?
# TODO: add date issue closed as well - can get that from API maybe?


issueProcess = ProcessIssues(
    org="pyopensci",
    repo_name="software-submission",
    label_name="6/pyOS-approved 🚀🚀🚀",
    API_TOKEN=API_TOKEN,
)

# Get all issues for approved packages
issues = issueProcess.return_response("lwasser")

# TODO: running into an error
# Loop through each issue and print the text in the first comment
review = {}
for issue in issues:
    package_name, body_data = issueProcess.parse_comment(issue)
    # index of 12 should include date accepted
    issue_meta = issueProcess.get_issue_meta(body_data, 12)
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

# TODO: make this a method too??
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


# TODO: this could be a base class that just exports to yaml - both
# classes can inherit and use this as well as the API token i think?
filename = "packages.yml"
with open(filename, "w") as file:
    # Create YAML object with RoundTripDumper to keep key order intact
    yaml = ruamel.yaml.YAML(typ="rt")
    # Set the indent parameter to 2 for the yaml output
    yaml.indent(mapping=4, sequence=4, offset=2)
    yaml.dump(review, file)
