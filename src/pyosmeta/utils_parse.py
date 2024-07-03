"""
A small module containing functions that support parsing
pyOpenSci review and contributor metadata.
"""

from pyosmeta.models import ReviewUser
from pyosmeta.utils_clean import clean_name


def parse_user_names(username: str) -> ReviewUser | None:
    """Parses authors, contributors, editors and usernames from
    the requested issues.

    Parameters
    ----------
    username : str
        The line with username (see Notes).

    Returns
    -------
    dict
        ``{name: str, github_username: str}``

    Notes
    -----
    Possible combinations:

    1. Name Surname (@Github_handle)
    2. (@Github_handle)
    3. @Github_handle

    """
    names = username.split("@", 1)
    names = [x for x in names if len(x) > 0]

    if len(names) > 1:
        parsed = {
            "github_username": clean_name(names[1]),
            "name": clean_name(names[0]),
        }
    elif len(names) == 0:
        return None
    else:
        parsed = {
            "github_username": clean_name(names[0]),
            "name": "",
        }

    return ReviewUser(**parsed)
