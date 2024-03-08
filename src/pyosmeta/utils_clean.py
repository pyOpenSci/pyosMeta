"""General cleaning utilities for markdown text.

We use these helpers to clean various markdown elements found in issue review text.
"""

import re
from datetime import datetime


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
