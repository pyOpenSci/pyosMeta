"""Data models for Contributors, Reviews, and GitHub metadata.

This module also includes a convenience class for URL validation.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Set, Union

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from pyosmeta.logging import logger
from pyosmeta.models.github import Labels
from pyosmeta.utils_clean import (
    check_url,
    clean_archive,
    clean_date,
    clean_markdown,
)


class Partnerships(str, Enum):
    astropy = "astropy"
    pangeo = "pangeo"


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
                logger.warning(
                    f"Oops, http protocol for {url}, changing to https"
                )
                url = url.replace("http://", "https://")
            elif not url.startswith("http"):
                logger.warning(
                    "Oops, missing http protocol for {url}, adding it"
                )
                url = "https://" + url
        if check_url(url=url):
            return url
        else:  # pragma: no cover
            logger.warning(f"Oops, url `{url}` is not valid, removing it")
            return None


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
    emeritus_editor: bool = Field(
        False, validation_alias=AliasChoices("emeritus_editor")
    )
    advisory: bool = False
    emeritus_advisory: bool = Field(
        False, validation_alias=AliasChoices("emeritus_advisory")
    )
    twitter: Optional[str] = Field(
        None, validation_alias=AliasChoices("twitter_username")
    )
    mastodon: Optional[str] = Field(
        None, validation_alias=AliasChoices("mastodon_username", "mastodon")
    )
    orcidid: Optional[str] = None
    partners: Optional[list[str]] = None
    website: Optional[str] = Field(
        None, validation_alias=AliasChoices("blog", "website")
    )
    board: Optional[bool] = False
    contributor_type: Set[str] = set()
    packages_eic: Set[str] = set()
    packages_editor: Set[str] = set()
    packages_submitted: Set[str] = set()
    packages_reviewed: Set[str] = set()
    location: Optional[str] = None
    email: Optional[str] = None

    @field_validator(
        "emeritus_advisory",
        "advisory",
        "emeritus_editor",
        "editorial_board",
        mode="before",
    )
    def validate_bool_fields(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        return False

    @field_validator(
        "packages_eic",
        "packages_reviewed",
        "packages_submitted",
        "packages_editor",
        "contributor_type",
        mode="before",
    )
    @classmethod
    def convert_to_set(cls, value: list[str]):
        """This method converts any list of things ingested into the
        model into a set object for cleaner parsing"""
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
        "packages_eic",
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
    description: Optional[str]
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


class ReviewUser(BaseModel):
    """Minimal model of a github user, used in several places in review parsing"""

    name: str | None
    github_username: str

    @field_validator("github_username", mode="after")
    def deurl_github_username(cls, github_username: str) -> str:
        return github_username.replace("https://github.com/", "")

    @field_validator("name", mode="after")
    def demarkdown_name(cls, name: str) -> str:
        return re.sub(r"\[|\]", "", name)


class ReviewModel(BaseModel):
    # Make sure model populates both aliases and original attr name
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    package_name: str | None = ""
    package_description: str = Field(
        "", validation_alias=AliasChoices("one-line_description_of_package")
    )
    submitting_author: ReviewUser | None = None
    all_current_maintainers: list[ReviewUser] = Field(default_factory=list)
    # Support presubmissions with an alias
    repository_link: str = Field(..., alias="repository_link_(if_existing)")
    version_submitted: Optional[str] = None
    categories: Optional[list[str]] = None
    editor: ReviewUser | list[ReviewUser] | None = None
    eic: ReviewUser | list[ReviewUser] | None = None
    reviewers: list[ReviewUser] = Field(default_factory=list)
    archive: str | None = None
    version_accepted: str | None = None
    date_accepted: str | None = Field(
        default=None,
        validation_alias=AliasChoices("Date accepted", "date_accepted"),
    )
    created_at: datetime = None
    updated_at: datetime = None
    closed_at: Optional[datetime] = None
    issue_link: str = None
    joss: Optional[str] = None
    partners: Optional[list[Partnerships]] = None
    gh_meta: Optional[GhMeta] = None
    labels: list[str] = Field(default_factory=list)
    active: bool = True  # To indicate if package is maintained or archived

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
        "categories",
        mode="before",
    )
    @classmethod
    def clean_categories(cls, categories: list[str]) -> list[str] | None:
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
        if categories is None:
            return None

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

    @field_validator("all_current_maintainers", mode="before")
    @classmethod
    def listify(cls, item: Any):
        """Make a field that's expected to be plural so before any validation"""
        if not isinstance(item, list):
            return [item]
        else:
            return item

    @field_validator("labels", mode="before")
    def extract_label(cls, labels: list[str | Labels]) -> list[str]:
        """
        Get just the ``name`` from the Labels model, if given
        """
        return [
            label.name if isinstance(label, Labels) else label
            for label in labels
        ]

    @field_validator(
        "archive",
        mode="before",
    )
    @classmethod
    def clean_archive(cls, archive: str) -> str:
        """Clean the archive value to ensure it's a valid archive URL."""
        return clean_archive(archive)

    @field_validator(
        "joss",
        mode="before",
    )
    @classmethod
    def clean_joss(cls, joss: str) -> str:
        """Clean the joss value to ensure it's a valid URL."""
        return clean_archive(joss)
