import urllib.request
from dataclasses import dataclass

import ruamel.yaml

# file io


@dataclass
class YamlIO:
    """
    A class that provides file output and cleanup methods.

    Parameters
    ----------
    """

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

    def clean_yaml_file(self, filename):
        """Open a yaml file and remove extra indents and spacing"""
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
