import requests

# Enter your GitHub username and API token here
USERNAME = "pyopensci"
# API_TOKEN = "your_token"

# Enter the name of the repository and the tag you want to search for
REPO_NAME = "software-submission"
TAG_NAME = "6/pyOS-approved 🚀🚀🚀"

# Set up the API endpoint
api_endpoint = (
    f"https://api.github.com/repos/{USERNAME}/{REPO_NAME}/issues?labels={TAG_NAME}"
)

# Make a GET request to the API endpoint
try:
    response = requests.get(api_endpoint, auth=(USERNAME, API_TOKEN))
except:
    print(f"Error: API request failed with status code {response.status_code}")


# Parse the JSON response to get a list of issues
issues = response.json()

# Loop through each issue and print the text in the first comment
for issue in issues:
    # Get the URL of the first comment
    comments_url = issue["comments_url"]
    body = issue["body"]

    lines = body.split("\r\n")
    body_data = [line.split(": ") for line in lines if line.strip() != ""]


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
