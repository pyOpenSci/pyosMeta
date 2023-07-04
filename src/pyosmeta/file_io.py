import os
import re
import urllib.request
from dataclasses import dataclass

import ruamel.yaml
from dotenv import load_dotenv

# file io


def get_api_token() -> str:
    """Fetches the GitHub API key from the .env file

    Returns
    -------
    str
        The provided API key in the .env file.
    """
    load_dotenv()
    return os.environ["GITHUB_TOKEN"]


@dataclass
class YamlIO:
    """
    A class that provides file output and cleanup methods.

    Parameters
    ----------
    """

    def dict_to_list(self, pyosDict: dict) -> list:
        """Turn dict into list for parsing to jekyll friendly yaml"""

        # Turn dict into list for parsing
        final_contribs = []
        for key in pyosDict:
            final_contribs.append(pyosDict[key])
        return final_contribs

    def open_yml_file(self, filename: str) -> dict:
        """Open & deserialize YAML file to dictionary.

        Parameters
        ----------
        filename : str
            Path to the YAML file to be opened.

        Returns
        -------
            Dictionary containing the structured data in the YAML file.
        """

        # TODO: this used to be self.web_yml so i'll need to reorganized
        # the contrib class
        with urllib.request.urlopen(filename) as f:
            return ruamel.yaml.safe_load(f)

    def export_yaml(self, filename: str, data_list: list):
        """Update website contrib file with the information grabbed from GitHub
        API

        Serialize contrib data from dictionary to YAML file.

        Parameters
        ----------

        filename : str
            Name of the output contributor filename ().yml format)
        data_list :  list
            A list containing contributor data for the website.

        Returns
        -------
        """

        with open(filename, "w") as file:
            # Create YAML object with RoundTripDumper to keep key order intact
            yaml = ruamel.yaml.YAML(typ="rt")
            yaml.default_flow_style = False
            # Set the indent parameter to 2 for the yaml output
            yaml.indent(mapping=4, sequence=4, offset=2)
            yaml.dump(data_list, file)

    def clean_string(self, astr: str) -> str:
        """
        Clean a string by removing occurrences of strings starting with "*id0" and "[]".

        Parameters
        ----------
        astr : str
            The string to be cleaned.

        Returns
        -------
        str
            The cleaned string.

        Examples
        --------
        >>> input_string = "packages-submitted: &id003 []"
        >>> clean_string(input_string)
        "packages-submitted: []"
        """
        patterns = ["*id001", "*id002", "*id003", "*id004"]
        # pattern = r"&id0\w{0,4}"
        for pattern in patterns:
            astr = astr.replace(pattern, "")
        return astr.replace("[]", "")

    def clean_yaml_file(self, filename):
        """Open a yaml file and remove extra indents and spacing"""
        with open(filename, "r") as f:
            lines = f.readlines()

        # TODO: regex would be cleaner here - https://stackoverflow.com/questions/27064964/python-replace-all-words-start-with
        cleaned_lines = []
        for i, line in enumerate(lines):
            if i == 0 and line.startswith("  "):
                # check for 2 spaces in the first line
                fix_indent = True
            if fix_indent:
                line = line.replace("  ", "", 1)
            line = self.clean_string(line)
            cleaned_lines.append(line)

        cleaned_text = "".join(cleaned_lines).replace("''", "")

        with open(filename, "w") as f:
            f.write(cleaned_text)

    def clean_export_yml(self, a_dict: dict, filename: str) -> None:
        """Inputs a dictionary with keys - contribs or packages.
        It then converse to a list for export, and creates a cleaned
        YAML file that is jekyll friendly
        """
        final_data = []
        for key in a_dict:
            final_data.append(a_dict[key])

        # Export to yaml
        self.export_yaml(filename, final_data)
        self.clean_yaml_file(filename)
