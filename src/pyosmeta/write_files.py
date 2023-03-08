from dataclasses import dataclass

# Do i want to use pyyaml instead?
import ruamel.yaml

# file io


@dataclass
class WriteYaml:
    """
    A class that provides file output and cleanup methods.

    Parameters
    ----------
    """

    def export_yaml(self, filename: str, data_dict: dict):
        """Update website contrib file with the information grabbed from GitHub
        API

        Serialize contrib data from dictionary to YAML file.

        Parameters
        ----------

        filename : str
            Name of the output contributor filename ().yml format)
        data_dict :  dict
            A dict containing contributor data for the website.

        Returns
        -------
        """

        with open(filename, "w") as file:
            # Create YAML object with RoundTripDumper to keep key order intact
            yaml = ruamel.yaml.YAML(typ="rt")
            # Set the indent parameter to 2 for the yaml output
            yaml.indent(mapping=4, sequence=4, offset=2)
            yaml.dump(data_dict, file)

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
