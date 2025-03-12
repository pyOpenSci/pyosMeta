import pickle
import urllib.request
from typing import Dict, List, Union

import ruamel.yaml
from ruamel.yaml import YAML

from .logging import logger


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


def create_paths(repos: Union[list[str], str]) -> Union[list[str], str]:
    """Construct URLs for .all-contributorsrc file on GitHub for pyos repos.

    We add new contributors to each repo using the all contributors bot. This
    generates urls for all of the files across all of our repos where people
    contribute to our content and processes.

    Parameters:
    ----------
    repos : Union[List[str], str]
        A list of GitHub repository names or a single repository name.

    Returns:
    -------
    Union[List[str], str]
        A list of URLs if `repos` is a list, or a single URL if `repos` is a string.
    """
    base_url = "https://raw.githubusercontent.com/pyOpenSci/"
    end_url = "/main/.all-contributorsrc"
    if isinstance(repos, list):
        all_paths = [base_url + repo + end_url for repo in repos]
    else:
        all_paths = base_url + repos + end_url

    return all_paths


def load_website_yml(key: str, url: str):
    """
    This opens a website contrib yaml file and turns it in a
    dictionary
    """
    yml_list = open_yml_file(url)

    return _list_to_dict(yml_list, key)


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
    try:
        with urllib.request.urlopen(file_path) as f:
            yaml = YAML(typ="safe", pure=True)
            return yaml.load(f)
    except urllib.error.URLError:
        logger.error(f"Oops - can find the url: {file_path}", exc_info=True)


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


def clean_string(astr: str) -> str:
    """
    Clean - remove strings starting with "*id0" and "[]".

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

    # TODO: regex would be cleaner here
    cleaned_lines = []
    fix_indent = False
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


def clean_export_yml(
    a_dict: Dict[str, Union[str, List[str]]] | List[dict], filename: str
) -> None:
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
