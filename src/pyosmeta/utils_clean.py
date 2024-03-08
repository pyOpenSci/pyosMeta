"""General cleaning utilities for markdown text.

We use these helpers to clean various markdown elements found in issue review text.
"""

import re
from datetime import datetime


def clean_date(a_date: str | None) -> datetime | str:
    """Cleans up a datetime from github and returns a date string

    In some cases the string is manually entered month-day-year and in
    others it's a gh time stamp. finally sometimes it could be missing
    or text. handle all of those cases with this validator.
    """

    if a_date is None or a_date == "missing":
        return "missing"
    else:
        try:
            return (
                datetime.strptime(a_date, "%Y-%m-%dT%H:%M:%SZ")
                .date()
                .strftime("%Y-%m-%d")
            )
        except TypeError as t_error:
            print("Oops - missing data. Setting date to missing", t_error)
            return "missing"


def clean_name(a_str: str) -> str:
    """Helper to strip unwanted chars from text"""

    unwanted = ["(", ")", "@"]
    for char in unwanted:
        a_str = a_str.replace(char, "")

    return a_str.strip()


def clean_markdown(txt: str) -> str:
    """
    Remove Markdown characters from the beginning or end of a string.

    Parameters
    ----------
    txt : str
        The input string containing Markdown characters.

    Returns
    -------
    str
        The input string with Markdown characters removed from the beginning
        and end.
    """

    pattern = r"^[`*]+|[`*]+$"

    # Use re.sub to remove the matched Markdown characters
    cleaned = re.sub(pattern, "", txt)

    return cleaned
