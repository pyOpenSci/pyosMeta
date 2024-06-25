"""General cleaning utilities for markdown text.

We use these helpers to clean various markdown elements found in issue review text.
"""

import re
from datetime import datetime
from typing import Any


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
        except TypeError as t_error:
            print("Oops - missing data. Setting date to missing", t_error)
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
