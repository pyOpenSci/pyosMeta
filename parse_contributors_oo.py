import json
import ruamel.yaml
import urllib.request
import requests


class processContributors:
    # When initializing how do you decide what should be an input
    # attribute vs just something a method accepted when called?
    def __init__(self, json_files: list, API_TOKEN: str):
        self.json_files = json_files
        self.API_TOKEN = API_TOKEN

    def process_json_file(self, json_file: str) -> dict:
        """Deserialize a JSON file from a URL and cleanup data

        Open a JSON file containing contributor data created from a all-contributors
        json file. Rename fields to match fields used in the website. Then
        add keys needed for the website.

        # TODO: if you use types do you need a docstring still with params?
        Parameters
        ----------
        json_file : string
            Web url of a json formatted file

        """
        response = requests.get(json_file)
        data = json.loads(response.text)

        # Create a dictionary to hold the processed data
        processed_data = {}
        # Loop through each entry in the JSON file
        for entry in data["contributors"]:
            # Check if the login value is already in the dictionary
            if entry["login"] not in processed_data:
                # Rename the login key to github_username
                entry["github_username"] = entry.pop("login")

                # Rename the profile key to website
                entry["website"] = entry.pop("profile")

                # Process github image avatar id
                entry["avatar_url"] = int(
                    entry["avatar_url"].rsplit("/", 1)[-1].rsplit("?", 1)[0]
                )
                entry["github_image_id"] = entry.pop("avatar_url")
                # Add empty values for the new keys
                for key in [
                    "mastodon",
                    "twitter",
                    "bio",
                    "orcidid",
                    "contributor_type",
                    "packages-submitted",
                    "packages-reviewed",
                ]:
                    entry[key] = ""

                # Add the entry to the processed data dictionary
                # NOTE: this adds the GH username as a key for each dict entry - might now want this
                processed_data[entry["github_username"]] = entry
        return processed_data

    # So here i think if i've instantiated the class with json files i can call it as self?
    def combine_json_data(self) -> dict:
        """deserialize and clean a list of json file url's."""
        # Create an empty dictionary to hold the combined data
        combined_data = {}

        # Loop through each JSON file
        for json_file in self.json_files:
            # Is this correct? do i call the method using self?
            # Process the JSON file and add the data to the combined dictionary
            data = self.process_json_file(json_file)
            combined_data.update(data)

        return combined_data

    # TODO: note that this returns a dict and the above a list so
    # it's inconsistent
    # All methods need self
    def get_gh_usernames(self, contrib_data: list) -> list:
        """Get a list of all gh usernames

        Parameters
        ----------
        contrib_data : list
            Dict containing all of the contributor information for the website.

        """
        all_usernames = []
        for item in contrib_data:
            all_usernames.append(item["github_username"])

        return all_usernames

    # TODO how do i know when i need to add self to an object?
    def get_user_info(self, username: str, API_TOKEN: str) -> dict:
        """
        Get a single user's information from their GitHub username
        # https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#get-the-authenticated-user

        Parameters
        ----------
        username : string
            Github username to retrieve data for

        API_TOKEN : string
            API token needed for auth to GitHub API

        Returns
        -------
            Dict with updated user data grabbed from the GH API
        """

        url = f"https://api.github.com/users/{username}"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(url, headers=headers)
        response_json = response.json()

        user_data = {}
        # TODO this could be created via a loop with a key:value pair to iterate over
        user_data[username] = {
            "location": response_json.get("location", None),
            "email": response_json.get("email", None),
            "twitter": response_json.get("twitter_username", None),
            "mastodon": response_json.get("mastodon_username", None),
            "organization": response_json.get("company", None),
            "website": response_json.get("blog", None),
            "bio": response_json.get("bio", None),
        }

        return user_data

    def get_gh_data(self, gh_usernames: list, API_TOKEN: str) -> list:
        """Parses through each github username and hits the GitHub
        API to grab user information.
        # This takes a minute as it's hitting the GitHub API

        Parameters
        ----------
        gh_usernames : list
            List of github usernames

        API_TOKEN : list

        Returns
        -------
            A list of updated user data via a list of github usernames
        """
        all_user_info = {}
        for gh_user in gh_usernames:
            print("Getting data for: ", gh_user)
            all_user_info[gh_user] = self.get_user_info(gh_user, API_TOKEN)
        return all_user_info

    def update_contrib_data(self, contrib_data, gh_data, update_keys):
        """Update contributor data from the GH API return.
        # GitHub will be the truth source for our contrib metadata here

        Parameters
        ----------
        user_data : dict
            All contributor data from the website
        update_keys : list
            List of string values representing the key value pair items to
            be updates
        """

        for i, item in enumerate(contrib_data):
            gh_name = item["github_username"]
            # Update the key:value pairs for data pulled from GitHub
            # Note that some data needs to be manual updated such as which
            # packages someone has reviewed. Cut if our team updates
            # the google doc or another file maybe i can automate that too?
            # TODO: I could parse github issues for reviewer names? and author names??!
            for akey in update_keys:
                # Stupid that the gh name is there twice??
                item[akey] = gh_data[gh_name][gh_name][akey]
        return contrib_data

    def format_url(self, url: str) -> str:
        """Append https to the beginning of URL if it doesn't exist
        If the url doesn't have https add it
        If the url starts with http change it to https
        Else do nothing

        Parameters
        ----------
        url : str
            String representing the url grabbed from the GH api

        """
        if not url:
            return url  # returns empty string if url is empty
        elif url.startswith("https://"):
            return url
        elif url.startswith("http://"):
            return "https://" + url[7:]
        else:
            return "https://" + url

    def create_new_contrib_file(self, filename: str, contrib_data: dict):
        """Update website contrib file with the information grabbed from GitHub
        API

        Serialize contrib data from dictionary to YAML file.

        Parameters
        ----------

        filename : str
            Name of the output contributor filename ().yml format)
        contrib_data :  dict
            A dict containing contributor data for the website.

        Returns
        -------
        """

        with open(filename, "w") as file:
            # Create YAML object with RoundTripDumper to keep key order intact
            yaml = ruamel.yaml.YAML(typ="rt")
            # Set the indent parameter to 2 for the yaml output
            yaml.indent(mapping=4, sequence=4, offset=2)
            yaml.dump(contrib_data, file)

    def clean_yaml_file(self, filename):
        """Open a yaml file and remove extra indent and spacing"""
        with open(filename, "r") as f:
            lines = f.readlines()

        cleaned_lines = []
        for line in lines:
            if line.startswith("  "):
                cleaned_lines.append(line[2:])
            else:
                cleaned_lines.append(line)

        cleaned_text = "".join(cleaned_lines).replace("''", "")

        with open(filename, "w") as f:
            f.write(cleaned_text)


"""Begin actual script """
# Get all contribs across repos
# Should this be an attribute in my class or is it better served as a list here?
json_files = [
    "https://raw.githubusercontent.com/pyOpenSci/python-package-guide/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/software-peer-review/main/.all-contributorsrc",
    "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/.all-contributorsrc",
]

# Get contribs from website
web_contrib_path = "https://raw.githubusercontent.com/pyOpenSci/pyopensci.github.io/main/_data/contributors.yml"


process_contribs = processContributors(json_files, API_TOKEN)
# Combine the cross-repo contribut data
all_contribs_dict = process_contribs.combine_json_data()

# Open the web contrib file (could also be a method)
with urllib.request.urlopen(web_contrib_path) as f:
    web_contrib_dict = ruamel.yaml.safe_load(f)

# Create a list of all gh usernames contributors from the website YAML
all_web_contribs = []
for item in web_contrib_dict:
    try:
        all_web_contribs.append(item["github_username"].lower())
    except:
        # Check if there is a missing gh username in our website listing
        print(item["name"], "is missing a github username")

# TODO: stopped work here!!

# Combine the web contrib with the cross-website contribs
# making sure the web content is first
# TODO: turn into function
for aitem in all_contribs_dict.keys():
    if aitem.lower() not in all_web_contribs:
        # Add index to dict
        web_contrib_dict.append(all_contribs_dict[aitem])

# Get a list of all gh usernames from the updated contrib data
# This can then be used to hit the GH api and update user metadata
all_gh_usernames = process_contribs.get_gh_usernames(web_contrib_dict)
# Now, update user data from GitHub profile via API - this will take a moment
# TODO: maybe add a processing bar to this
gh_data = process_contribs.get_gh_data(all_gh_usernames, API_TOKEN)

# Update user yaml file data from GitHub API
update_keys = ["twitter", "website", "location", "bio", "organization", "email"]
final_filename = "contributors.yml"


updated_contrib = process_contribs.update_contrib_data(
    web_contrib_dict, gh_data, update_keys
)

# Clean website urls make sure it starts with https
for i, item in enumerate(updated_contrib):
    item["website"] = process_contribs.format_url(item["website"])


# Create final updated YAML file from the updated data above and clean that file
# to match the website
process_contribs.create_new_contrib_file(
    filename=final_filename, contrib_data=updated_contrib
)
process_contribs.clean_yaml_file(final_filename)
