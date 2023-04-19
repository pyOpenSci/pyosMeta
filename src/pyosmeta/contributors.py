import json
from dataclasses import dataclass

import requests

from .file_io import YamlIO

# SOLID guidelines to improve code


@dataclass
class ProcessContributors(YamlIO):
    # When initializing how do you decide what should be an input
    # attribute vs just something a method accepted when called?
    def __init__(self, json_files: list, web_yml: str, API_TOKEN: str):
        """
        Parameters
        ----------

        json_files : list
            A list of string objects each of which represents a URL to a JSON
            file to be parsed
        web_yml : str
            A string containing a path to a online website yml file
            This file contains contributor data used to build the website contribs list
        API_TOKEN : str
            A string containing your API token needed to access the github API
        """

        self.json_files = json_files
        self.API_TOKEN = API_TOKEN
        self.web_yml = web_yml
        self.update_keys = [
            "twitter",
            "website",
            "location",
            "bio",
            "organization",
            "email",
            "name",
            "github_image_id",
            "github_username",
        ]
        self.contrib_template = {
            "name": "",
            "bio": "",
            "organization": "",
            "title": "",
            "github_username": "",
            "github_image_id": "",
            "editorial-board": "",
            "twitter": "",
            "mastodon": "",
            "orcidid": "",
            "website": "",
            "contributor_type": "",
            "packages-editor": "",
            "packages-submitted": "",
            "packages-reviewed": "",
            "location": "",
            "email": "",
        }

    def _list_to_dict(self, aList: list) -> dict:
        """Takes a yaml file opened and turns into a dictionary
        The dict structure is key (gh_username) and then a dictionary
        containing all information for the username

        aList : list
            A list of dictionary objects returned from load website yaml

        """
        final_dict = {}
        for dict in aList:
            final_dict[dict["github_username"]] = dict
        return final_dict

    # TODO: this is io stuff...
    def load_website_yml(self):
        """
        This opens a website contrib yaml file and turns it in a
        dictionary
        """
        yml_list = self.open_yml_file(self.web_yml)
        return self._list_to_dict(yml_list)

    def process_json_file(self, json_file: str) -> dict:
        """Deserialize a JSON file from a URL and cleanup data

        Open a JSON file containing contributor data created from a all-contributors
        json file. Rename fields to match fields used in the website. Then
        add keys needed for the website.

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
        # TODO: SOLID - avoid massive structures with conditional statements
        for entry in data["contributors"]:
            # Check if the login value is already in the dictionary
            if entry["login"] in processed_data:
                # Continue will go to the next iteration in a loop
                continue
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
            # TODO: Tuple - consumes less memory -- ("mastodon",
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
            # NOTE: this adds the GH username as a key for each dict entry
            processed_data[entry["github_username"]] = entry
        return processed_data

    def combine_json_data(self) -> dict:
        """Deserialize and clean a list of json file url's.

        Returns
        -------
            Dictionary containing json data for all contributors across
            the website
        """
        # Create an empty dictionary to hold the combined data
        combined_data = {}

        # Loop through each JSON file
        for json_file in self.json_files:
            # Is this correct? do i call the method using self?
            # Process the JSON file and add the data to the combined dictionary
            try:
                data = self.process_json_file(json_file)
                combined_data.update(data)
            except:
                print("Oops - can't process", json_file)

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
    def get_user_info(self, username: str) -> dict:
        """
        Get a single user's information from their GitHub username
        # https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#get-the-authenticated-user

        Parameters
        ----------
        username : string
            Github username to retrieve data for

        Returns
        -------
            Dict with updated user data grabbed from the GH API
        """

        url = f"https://api.github.com/users/{username}"
        headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        response = requests.get(url, headers=headers)
        response_json = response.json()

        user_data = {}
        # TODO this could be created via a loop with a key:value pair to iterate over
        # I wonder if i can do this with a single .get()
        user_data[username] = {
            "name": response_json.get("name", None),
            "location": response_json.get("location", None),
            "email": response_json.get("email", None),
            "twitter": response_json.get("twitter_username", None),
            "mastodon": response_json.get("mastodon_username", None),
            "organization": response_json.get("company", None),
            "website": response_json.get("blog", None),
            "bio": response_json.get("bio", None),
            "github_image_id": response_json.get("id", None),
            "github_username": response_json.get("login", None),
        }

        return user_data

    def combine_users(self, repoDict: dict, webDict: dict) -> dict:
        """
        Method that combines website yaml users with contribs across
        other repos into a single dictionary

        Parameters
        ----------

        repoDict: dict
            Dictionary representing the deserialized json data contained
            in the all-contributors .json file located in each of our
            repositories.

        webDict: dict
            Dictionary representing the deserialized YAML data parsed from
            the website YAML contributors file.

        Returns
        -------



        """

        # Turn webDict keys
        web_usernames = [key.lower() for key in webDict.keys()]

        for aitem in repoDict.keys():
            if aitem.lower() not in web_usernames:
                # Add index to dict
                print("adding: ", aitem)
                webDict[aitem] = repoDict[aitem]
        return webDict

    def add_new_user(self, gh_user: str) -> dict:
        """Add a new user to the contrib file using gh username

        This method does a few things.
        1. Adds a new template entry for the user w no values populated
        2. Gets user metadata from the user's github profile
        3. Updates their contrib entry with the gh data

        """
        new = {}
        new[gh_user] = self.contrib_template.copy()
        gh_data = self.get_gh_data([gh_user])
        # Update their metadata in the dict and return
        # It's updating the contrib dict object in this method why?
        updated_data = self.update_contrib_data(new, gh_data)
        return updated_data

    def get_gh_data(self, gh_usernames: list) -> list:
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
            print("Getting github data for: ", gh_user)
            all_user_info[gh_user] = self.get_user_info(gh_user)
        return all_user_info

    def _check_url(self, url: str) -> bool:
        """Test a url and return true if it works, false if not

        Parameters
        ----------
        url : str
            String for a url to a website to test.

        """

        try:
            response = requests.get(url, timeout=6)
            return response.status_code == 200
        except:
            print("Oops, url", url, "is not valid, removing it")
            return False

    def update_contrib_data(self, contrib_data: dict, gh_data: dict):
        """Update contributor data from the GH API return.

        Use the GitHub API to grab user profile data such as twitter handle,
        mastodon, website, email and location and update contributor
        information. GitHub profile data is the source of truth source for
        contributor metadata.

        Parameters
        ----------
        contrib_data : dict
            A dict containing contributor data to be updated
        gh_data : dict
            Updated contributor data pulled from github API
        """

        for i, gh_name in enumerate(contrib_data.keys()):
            print(i, gh_name)
            # Assign gh username
            # Update the key:value pairs for data pulled from GitHub
            # Note that some data needs to be manual updated such as which
            # packages someone has reviewed.
            for akey in self.update_keys:
                print(akey)
                if akey == "website":
                    url = gh_data[gh_name][gh_name][akey]
                    # Fix the url format and check to see if it works online
                    url = self.format_url(url)
                    # It url is valid, add to dict
                    print("Checking: ", url)
                    if self._check_url(url):
                        contrib_data[gh_name][akey] = url
                    else:
                        contrib_data[gh_name][akey] = ""
                else:
                    contrib_data[gh_name][akey] = gh_data[gh_name][gh_name][akey]

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
        print("fixing", url)
        if not url:
            return url  # returns empty string if url is empty
        elif url.startswith("https://"):
            print("https already, no fix needed", url)
            return url
        elif url.startswith("http://"):
            print("fixing", url, "https://" + url[7:])
            return "https://" + url[7:]
        else:
            print("fixing", url)
            return "https://" + url
