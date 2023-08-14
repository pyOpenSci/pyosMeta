import pickle
import urllib.request
from typing import Dict, List, Optional, Tuple, Union

import ruamel.yaml


def load_pickle(filename):
    """Opens a pickle"""
    with open(filename, "rb") as f:
        return pickle.load(f)


def _list_to_dict(a_list: List, a_key: str) -> Dict:
    """Takes a yaml file opened and turns into a dictionary
    The dict structure is key (gh_username) and then a dictionary
    containing all information for the username

    a_list : list
        A list of dictionary objects returned from load website yaml
    a_key : str
        A string representing the dict key to use as the main key to call
        each sub dict in the object.

    """

    return {a_dict[a_key].lower(): a_dict for a_dict in a_list}


def load_website_yml(key: str, url: str):
    """
    This opens a website contrib yaml file and turns it in a
    dictionary
    """
    yml_list = open_yml_file(url)

    return _list_to_dict(yml_list, key)


# def dict_to_list(pyos_meta: Dict[str, Union[str, List[str]]]) -> List[Dict]:
#     """Turn dict into list for parsing to jekyll friendly yaml

#     Parameters
#     ----------
#     pyos_meta : Dict
#         A dictionary containing metadata for pyos contributors or review issues

#     Returns
#     -------
#     List
#         A list of dictionaries containing pyos metadata for contribs or reviews

#     """
#     print("a")
#     # Turn dict into list for parsing
#     return [pyos_meta[key] for key in pyos_meta]
#     # for key in pyos_meta:
#     #     final_contribs.append(pyos_meta[key])
#     # return final_contribs


def open_yml_file(file_path: str) -> dict:
    """Open & deserialize YAML file to dictionary.

    Parameters
    ----------
    file_path : str
        Path to the YAML file to be opened.

    Returns
    -------
        Dictionary containing the structured data in the YAML file.
    """

    # TODO: this used to be self.web_yml so i'll need to reorganized
    # the contrib class
    with urllib.request.urlopen(file_path) as f:
        return ruamel.yaml.safe_load(f)


def export_yaml(filename: str, data_list: list):
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


# TODO: Double check - i may be able to combine this with the other clean
# function created
def clean_string(astr: str) -> str:
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


def clean_yaml_file(filename):
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
        line = clean_string(line)
        cleaned_lines.append(line)

    cleaned_text = "".join(cleaned_lines).replace("''", "")

    with open(filename, "w") as f:
        f.write(cleaned_text)


def clean_export_yml(a_dict: Dict[str, Union[str, List[str]]], filename: str) -> None:
    """Inputs a dictionary with keys - contribs or packages.
    It then converse to a list for export, and creates a cleaned
    YAML file that is jekyll friendly

    Parameters
    ----------
    a_dict : Dict
        A dictionary containing final pyos metadata information
    filename : str
        Name of the YML file to export

    Returns
    -------
    None
        Outputs a yaml file with the input name containing the pyos meta
    """

    # Export to yaml
    export_yaml(filename, a_dict)
    clean_yaml_file(filename)
