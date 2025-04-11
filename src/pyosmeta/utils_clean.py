"""General cleaning utilities for markdown text.

We use these helpers to clean various markdown elements found in issue review text.
"""

import re
from datetime import datetime
from typing import Any

import doi
import requests

from .logging import logger


def get_clean_user(username: str) -> str:
    """Cleans a GitHub username provided in a review issue by removing any
    additional text after a space and converting to lowercase.

    This function assumes that a valid username should not contain spaces. If a
    space is detected, only the part before the first space is considered the
    username. The resulting string is then trimmed of whitespace and converted
    to lowercase.

    Parameters
    ----------
    username : str
        The input username string which may contain extra text or spaces.

    Returns
    -------
    str
        The cleaned username in lowercase without any extra text or spaces.

    Examples
    --------
    >>> get_clean_user("@githubusername")
    'githubusername'

    >>> get_clean_user("@githubusername name after text")
    'githubusername'
    """

    if len(username.split()) > 1:
        username = username.split()[0]
    return username.lower().strip()


def clean_date(source_date: str | None) -> datetime | str:
    """Cleans up a date string to a consistent datetime format.

    The source date string may have been manually entered as month-day-year format,
    retrieved from GitHub as a timestamp, could be missing, or contain random text.
    This utility validates the input and returns a consistent format.
    """

    if source_date is None or source_date == "missing":
        return "missing"
    else:
        try:
            return (
                datetime.strptime(source_date, "%Y-%m-%dT%H:%M:%SZ")
                .date()
                .strftime("%Y-%m-%d")
            )
        except TypeError:
            logger.error(
                "Oops - missing date. Setting date to 'missing'", exc_info=True
            )
            return "missing"


def clean_name(source_name: str) -> str:
    """Remove unwanted characters from a name."""

    unwanted = ["(", ")", "@"]
    for char in unwanted:
        source_name = source_name.replace(char, "")

    return source_name.strip()


def clean_markdown(source_text: str) -> str:
    """
    Cleans unwanted Markdown characters from text and returns cleaned text.

    Parameters
    ----------
    source_text : str
        The input string containing Markdown characters.

    Returns
    -------
    str
        The input string with Markdown characters removed from the beginning
        and end.
    """

    pattern = r"^[`*]+|[`*]+$"

    # Use re.sub to remove the matched Markdown characters
    cleaned = re.sub(pattern, "", source_text)

    return cleaned


def clean_date_accepted_key(review_dict: dict[str, Any]) -> dict[str, str]:
    """
    Normalize date_accepted keys in our review dictionary.

    In our reviews we have various templates that have evolved over the past
    5 years (since 2019). Some used date accepted, some have date accepted
    (month/day/year) and some have month-day-year. Rather than try to
    account for all of these this is a helper that simply updates the key
    to be date_accepted regardless of what is found after that text.

    Parameters
    ----------
    review_dict : dict
        Dictionary containing date_accepted key and other review data.

    Returns
    -------
    dict
        The modified review dictionary with normalized date_accepted key.
    """
    for key in list(review_dict.keys()):
        if key.startswith("date_accepted"):
            # Remove the old key
            value = review_dict.pop(key)
            # Add the new key with the value
            review_dict["date_accepted"] = value
            break
    return review_dict


def check_url(url: str) -> bool:
    """Test url. Return true if there's a valid response, False if not

    Parameters
    ----------
    url : str
        String for a url to a website to test.

    """

    try:
        response = requests.get(url, timeout=6)
        return response.status_code == 200
    except Exception:  # pragma: no cover
        return False


def is_doi(archive) -> str | None:
    """Check if the DOI is valid and return the DOI link.

    Parameters
    ----------
    archive : str
        The DOI string to validate, e.g., `10.1234/zenodo.12345678`

    Returns
    -------
    str | None
        The DOI link in the form `https://doi.org/10.1234/zenodo.12345678` or `None`
        if the DOI is invalid.
    """
    try:
        return doi.validate_doi(archive)
    except ValueError:
        pass


def clean_archive(archive):
    """Clean an archive link to ensure it is a valid DOI URL.

    This utility will attempt to parse the DOI link from the various formats
    that are commonly present in review metadata. This utility will handle:

    * Markdown links in the format `[label](URL)`, e.g., `[my archive](https://doi.org/10.1234/zenodo.12345678)`
    * Raw text in the format `DOI` e.g., `10.1234/zenodo.12345678`
    * URLs in the format `http(s)://...` e.g., `https://doi.org/10.1234/zenodo.12345678`
    * The special cases `n/a` and `tbd` which will be returned as `None` in anticipation of future data

    If the archive link is a URL, it will be returned as is with a check that
    it resolves but is not required to be a valid DOI. If the archive link is
    a DOI, it will be validated and returned as a URL in the form
    `https://doi.org/10.1234/zenodo.12345678` using the `python-doi` package.

    """
    archive = archive.strip()  # Remove leading/trailing whitespace
    if not archive:
        # If field is empty, return None
        return None
    if archive.startswith("[") and archive.endswith(")"):
        # Extract the outermost link
        link = archive[archive.rfind("](") + 2 : -1]
        # recursively clean the archive link
        return clean_archive(link)
    elif link := is_doi(archive):
        # is_doi returns the DOI link if it is valid
        return link
    elif archive.startswith("http"):
        if archive.startswith("http://"):
            archive = archive.replace("http://", "https://")
        # Validate that the URL resolves
        if not check_url(archive):
            raise ValueError(f"Invalid archive URL (not resolving): {archive}")
        return archive
    elif archive.lower() == "n/a":
        return None
    elif archive.lower() == "tbd":
        return None
    else:
        raise ValueError(f"Invalid archive URL: {archive}")
