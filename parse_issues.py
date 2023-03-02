import requests

# Enter your GitHub username and API token here
USERNAME = "pyopensci"
# API_TOKEN = "your_token"

# Enter the name of the repository and the tag you want to search for
REPO_NAME = "software-submission"
TAG_NAME = "6/pyOS-approved 🚀🚀🚀"

# Set up the API endpoint
api_endpoint = (
    f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/issues?labels={TAG_NAME}&state=all"
)

# Make a GET request to the API endpoint
try:
    response = requests.get(api_endpoint, auth=(USERNAME, API_TOKEN))
except:
    print(f"Error: API request failed with status code {response.status_code}")


# Parse the JSON response to get a list of issues
issues = response.json()

def contains_keyword(string):
    return string.startswith(("Submitting", "Editor", "Reviewer"))

# Loop through each issue and print the text in the first comment
review = {}
for issue in issues:
    # Get the URL of the first comment
    comments_url = issue["comments_url"]
    body = issue["body"]

    lines = body.split("\r\n")
    body_data = [line.split(": ") for line in lines if line.strip() != ""]

    # Loop through issue header and grab relevant review metadata
    package_name = body_data[1][1]
    print(package_name)
    review_meta = {}
    for item in body_data[0:11]: 
        if contains_keyword(item[0]):
            names = item[1].split("(", 1)
            if len(names) > 1:
                review_meta[item[0]] = {"name": names[0].strip(), "github_username":names[1].strip().lstrip("@").rstrip(")")}
            else: 
                review_meta[item[0]] = {"name": "", "github_username": names[0].strip().lstrip("@")}
        else:
            if len(item) > 1:
                review_meta[item[0]] = item[1]
    review[package_name] = review_meta

### GET REPOSITORY METADATA FOR ACCEPTED PACKAGES ###
# TODO: some issues say repository link (if existing) and others just say repository link
# FIx this in the issues but also will have to rerun code above... 
# Get a list of github repos for reviews 
all_repos = []
for aPackage in review.keys():
    print(aPackage)
    repo = review[aPackage]["Repository Link"]
    owner, repo = repo.split('/')[-2:]
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    all_repos.append(repo_url)

# TODO:
# Add date accepted to the issue
# add date issue closed as well - can get that from API maybe?
# Get the docs url from the repository link (API query)

# Construct the API endpoint URL using the repository information
#url = f"https://api.github.com/repos/earthlab/earthpy"


# Send a GET request to the API endpoint and include a user agent header
gh_stats = ["description",
            "homepage", 
            'created_at',
            'stargazers_count', 
            'watchers_count',
            'stargazers_count', 
            'forks', 
            'open_issues_count', 
            "forks_count"]

def get_repo_meta(url: str, stats_list: list)-> dict:
    stats_dict = {}
    # Small script to get the url (normally the docs) and description of a repo!
    response = requests.get(url)

    # Extract the description and homepage URL from the response JSON
    data = response.json()
    for astat in stats_list:
        print(astat)
        stats_dict[astat] =  data[astat]

    return stats_dict

# TODO failing on description key - not sure why!
all_repo_meta = []
for repo in all_repos:
    print(repo)
    all_repo_meta.append(get_repo_meta(repo, gh_stats))



# Get contributor counts information
url = url+"/contributors"
response = requests.get(url)

data = response.json()

# Get the number of contributors from the response headers
total_contributors = int(response.headers['X-Total-Count'])

# Print the total number of contributors
print(f'Total contributors: {total_contributors}')


# Last commit date and time
url = f'https://api.github.com/repos/{owner}/{repo}/commits'
headers = {'Authorization': f'token {access_token}'}
response = requests.get(url, headers=headers)

# Parse the JSON response and get the last commit date
data = json.loads(response.text)
last_commit_date = data[0]['commit']['author']['date']
last_commit_date = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%SZ')

# Print the last commit date in a human-readable format
print('Last commit date:', last_commit_date.strftime('%B %d, %Y %I:%M:%S %p'))
"""
Add: to data 
  date-accepted: 2021-12-29
  highlight:
  docs-url: "https://jointly.readthedocs.io"
  citation-link:
"""
# Create dict with info
# Using create contrib file method from other script 
filename = "packages.yml"
with open(filename, "w") as file:
    # Create YAML object with RoundTripDumper to keep key order intact
    yaml = ruamel.yaml.YAML(typ="rt")
    # Set the indent parameter to 2 for the yaml output
    yaml.indent(mapping=4, sequence=4, offset=2)
    yaml.dump(review, file)

  
  """
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



def parse_issue():
    sections = body.split('\r\n')

def get_package_name():
    # Get the package name from the first section

# Create dictionary of metadata for the issue
all_packages = {}

# Create method to parse single issue
issue_meta = {}
for line in lines[0:11]:
    key, value = line.split(": ")
    issue_meta[key] = value

all_packages[issue_meta["Package Name"]] = issue_meta


    # Make a GET request to the comments URL
    # comments_response = requests.get(comments_url, auth=(USERNAME, TOKEN))

    # # Check if the request was successful
    # if comments_response.status_code != 200:
    #     print(
    #         f"Error: API request failed with status code {comments_response.status_code}"
    #     )
    #     continue

    # Parse the JSON response to get a list of comments
    comments = comments_response.json()

    # Check if there are any comments
    if len(comments) == 0:
        continue

    # Get the text of the first comment
    first_comment_text = comments[0]["body"]

    # Print the text of the first comment
    print(f"Text of first comment in issue #{issue['number']}:")
    print(first_comment_text)
