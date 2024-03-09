"""Data models for Contributors, Reviews, and GitHub metadata.

This module also includes a convenience class for URL validation.
"""

import re

import requests
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from typing import Optional, Set, Union

from pyosmeta.utils_clean import clean_date, clean_markdown


class UrlValidatorMixin:
    """A mixin to validate classes that are of the same type across
    several models.

    """

    @field_validator(
        "website", "documentation", mode="before", check_fields=False
    )
    @classmethod
    def format_url(cls, url: str) -> str:
        """Append https to the beginning of URL if it doesn't exist & cleanup
        If the url doesn't have https add it
        If the url starts with http change it to https
        Else do nothing

        Parameters
        ----------
        url : str
            String representing the url grabbed from the GH api

        """

        if not url:
            return url  # Returns empty string if url is empty
        else:
            if url.startswith("http://"):
                print(f"{url} 'http://' replacing w 'https://'")
                url = url.replace("http://", "https://")
            elif not url.startswith("http"):
                print("Oops, missing http")
                url = "https://" + url
        if cls._check_url(url=url):
            return url
        else:
            return None

    @staticmethod
    def _check_url(url: str) -> bool:
        """Test url. Return true if there's a valid response, False if not

        Parameters
        ----------
        url : str
            String for a url to a website to test.

        """

        try:
            response = requests.get(url, timeout=6)
            return response.status_code == 200
        except Exception:
            print("Oops, url", url, "is not valid, removing it")
            return False


class PersonModel(BaseModel, UrlValidatorMixin):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    name: str | None = None
    github_username: str = Field(None, validation_alias=AliasChoices("login"))
    github_image_id: int = Field(None, validation_alias=AliasChoices("id"))
    title: Optional[Union[list[str], str]] = None
    sort: int | None = None
    bio: Optional[str] = None
    organization: Optional[str] = Field(
        None, validation_alias=AliasChoices("company")
    )
    date_added: Optional[str] = ""
    deia_advisory: Optional[bool] = False
    editorial_board: Optional[bool] = Field(
        None, validation_alias=AliasChoices("editorial-board")
    )
    advisory: Optional[bool] = False
    twitter: Optional[str] = Field(
        None, validation_alias=AliasChoices("twitter_username")
    )
    mastodon: Optional[str] = Field(
        None, validation_alias=AliasChoices("mastodon_username", "mastodon")
    )
    orcidid: Optional[str] = None
    website: Optional[str] = Field(
        None, validation_alias=AliasChoices("blog", "website")
    )
    board: Optional[bool] = False
    contributor_type: Set[str] = set()
    packages_editor: Set[str] = set()
    packages_submitted: Set[str] = set()
    packages_reviewed: Set[str] = set()
    location: Optional[str] = None
    email: Optional[str] = None

    @field_validator(
        "packages_reviewed",
        "packages_submitted",
        "packages_editor",
        "contributor_type",
        mode="before",
    )
    @classmethod
    def convert_to_set(cls, value: list[str]):
        if isinstance(value, list):
            if not value:
                return set()
            elif value[0] is None:
                return set()
            else:
                value = [a_val.lower() for a_val in value]
                return set(value)
        elif value is None:
            return set()
        return set(value.lower())

    def add_unique_value(self, attr_name: str, values: Union[str, list[str]]):
        """A helper that will add only unique values to an existing list"""
        if isinstance(values, str):
            values = [values]
        attribute = getattr(self, attr_name)
        if isinstance(attribute, set):
            attribute.update(values)
        else:
            raise ValueError(f"{attr_name} is not a set attribute")

    @field_serializer(
        "packages_reviewed",
        "packages_submitted",
        "packages_editor",
        "contributor_type",
    )
    def serialize_set(self, items: Set[str]):
        """This is a serializer that runs on export. It ensures sets are
        converted to lists"""
        return sorted(list(items))

    @field_validator("bio", mode="before")
    @classmethod
    def clean_strings(cls, string: str) -> str:
        """This is a cleaning step that will remove spurious
        characters from string fields.

        """
        if isinstance(string, str):
            string = re.sub(r"[\r\n]", "", string)
        return string


class GhMeta(BaseModel, UrlValidatorMixin):
    name: str
    description: str
    created_at: str
    stargazers_count: int
    watchers_count: int
    open_issues_count: int
    forks_count: int
    documentation: Optional[str]
    contrib_count: int
    last_commit: str

    @field_validator(
        "last_commit",
        "created_at",
        mode="before",
    )
    @classmethod
    def clean_date(cls, a_date: Optional[str]) -> str:
        """Cleans up a datetime from github and returns a date string

        Runs the general clean_date function in this module as a validator.
        """

        return clean_date(a_date)


class ReviewModel(BaseModel):
    # Make sure model populates both aliases and original attr name
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    package_name: str | None = ""
    package_description: str = Field(
        "", validation_alias=AliasChoices("one-line_description_of_package")
    )
    submitting_author: dict[str, str | None] = {}
    all_current_maintainers: list[dict[str, str | None]] = {}
    repository_link: str | None = None
    version_submitted: Optional[str] = None
    categories: Optional[list[str]] = None
    editor: dict[str, str | None] = {}
    reviewer_1: dict[str, str | None] = {}
    reviewer_2: dict[str, str | None] = {}
    archive: str | None = None
    version_accepted: str | None = None
    date_accepted: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "date_accepted_(month/day/year)", "Date accepted", "date_accepted"
        ),
    )
    created_at: str = None
    updated_at: str = None
    closed_at: Optional[str] = None
    issue_link: str = None
    joss: Optional[str] = None
    partners: Optional[list[str]] = None
    gh_meta: Optional[GhMeta] = None

    @field_validator(
        "date_accepted",
        mode="before",
    )
    @classmethod
    def clean_date_review(cls, a_date: Optional[str]) -> str:
        """Clean a manually added datetime that is added to a review by an
        editor when the review package is accepted.

        """
        if a_date is None or a_date in ["missing", "TBD"]:
            return "missing"
        else:
            new_date = a_date.replace("/", "-").split("-")
            if len(new_date[0]) == 4:
                return f"{new_date[0]}-{new_date[1]}-{new_date[2]}"
            else:
                return f"{new_date[2]}-{new_date[0]}-{new_date[1]}"

    @field_validator(
        "created_at",
        "updated_at",
        "closed_at",
        mode="before",
    )
    @classmethod
    def clean_date(cls, a_date: Optional[str]) -> str:
        """Cleans up a datetime from github and returns a date string

        Runs the general clean_date function in this module as a validator.

        """

        return clean_date(a_date)

    @field_validator(
        "package_name",
        mode="before",
    )
    @classmethod
    def clean_pkg_name(cls, pkg_name: str) -> str:
        """A small cleaning step to remove any additional markdown
        from a package's name

        Parameters
        ----------
        pkg_name : str
            Name of a pyOpenSci package extracted from review issue title

        Returns
        -------
        str
            Cleaned string with any markdown formatting removed.
        """

        return clean_markdown(pkg_name)

    @field_validator(
        "repository_link",
        mode="before",
    )
    @classmethod
    def clean_markdown_url(cls, repo: str) -> str:
        """Remove markdown link remnants from gh usernames and name.

        Sometimes editors and reviewers add names using github links.
        Remove the link data.
        """

        if repo.startswith("["):
            return repo.split("](")[0].replace("[", "")
        else:
            return repo

    @field_validator(
        "editor",
        "reviewer_1",
        "reviewer_2",
        mode="before",
    )
    @classmethod
    def clean_gh_url(cls, user: dict[str, str]) -> dict[str, str]:
        """Remove markdown link remnants from gh usernames and name.

        Sometimes editors and reviewers add names using github links.
        Remove the link data.
        """

        user["github_username"] = user["github_username"].replace(
            "https://github.com/", ""
        )
        user["name"] = re.sub(r"\[|\]", "", user["name"])

        return user

    @field_validator(
        "categories",
        mode="before",
    )
    @classmethod
    def clean_categories(cls, categories: list[str]) -> list[str]:
        """Make sure each category in the list is a valid value.

        Valid pyos software categories are:
            citation-management-bibliometrics, data-deposition,
            data-extraction, data-processing-munging, data-retrieval,
            data-validation-testing, data-visualization-analysis,
            database-interoperability, education,
            geospatial, scientific-software-wrappers,
            workflow-automation-versioning


        Parameters
        ----------
        categories : list[str]
            List of categories to clean.

        Returns
        -------
        list[str]
            List of cleaned categories.
        """

        valid_categories = {
            "data-processing": "data-processing-munging",
            "data-validation": "data-validation-testing",
            "scientific-software": "scientific-software-wrapper",
        }

        cleaned_cats = []
        for category in categories:
            for valid_prefix, valid_cat in valid_categories.items():
                if category.startswith(valid_prefix):
                    cleaned_cats.append(valid_cat)
                    break
            else:
                # No match found, keep the original category
                cleaned_cats.append(category)
        return cleaned_cats
