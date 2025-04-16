import re
import traceback
from dataclasses import dataclass
from typing import Any, List, Union

from pydantic import ValidationError
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from pyosmeta.models import ReviewModel, ReviewUser
from pyosmeta.models.github import Issue, Labels, LabelType

from .github_api import GitHubAPI
from .logging import logger
from .utils_clean import clean_date_accepted_key
from .utils_parse import parse_user_names

KEYED_STRING = re.compile(r"\s*(?P<key>\S*?)\s*:\s*(?P<value>.*)\s*")
"""
Parse a key-value string into keys and values.

Examples:

    >>> text = 'Astropy: Link coming soon to standards'
    >>> KEYED_STRING.search(text).groupdict()
    {'key': 'Astropy', 'value': 'Link coming soon to standards'}
"""


@dataclass
class ProcessIssues:
    """
    A class that processes GitHub issues in our peer review process and returns
    metadata about each package.
    """

    def __init__(self, github_api: GitHubAPI):
        """
        Initialize a process issues instance.

        Parameters
        ----------
        github_api : str
            Instantiated instance of a GitHubAPI object
        """

        self.github_api = github_api

    def get_issues(self) -> list[Issue]:
        """
        Call return response in GitHub api object.

        Returns a list of dictionaries representing issues.

        Returns
        -------
        list
            List of dict items each containing a review issue

        Notes
        -----
        We add a filter here to labels because the github api defaults to
        grabbing issues with ALL using an and operator labels in a list. We
        need to use an OR as a selector.
        """

        url = self.github_api.api_endpoint
        issues = self.github_api._get_response_rest(url)

        # Filter issues according to label query value
        labels = self.github_api.labels
        filtered_issues = [
            issue
            for issue in issues
            if any(label["name"] in labels for label in issue["labels"])
        ]

        return [Issue(**i) for i in filtered_issues]

    def _is_review_role(self, string: str) -> bool:
        """
        Returns true if starts with any of the 3 items below.
        """
        return any(
            [
                substr in string.lower()
                for substr in (
                    ("submitting", "editor", "eic", "reviewer", "maintainers")
                )
            ]
        )

    def _remove_extra_chars(self, a_str: str) -> str:
        """Helper to strip unwanted characters from text"""

        unwanted = ["(", ")", "@"]
        for char in unwanted:
            a_str = a_str.replace(char, "")

        return a_str.strip()

    def _split_header(self, body: str) -> tuple[str, str]:
        """
        Split an issue body into the header and the body using ---,
        joining the body remainder if there are extra unexpected ---'s
        """
        parts = body.split("---")
        if len(parts) > 2:
            body_remainder = "---".join(parts[1:])
        elif len(parts) == 1:
            # eg. if we just have a header
            return parts[0], ""
        else:
            body_remainder = parts[1]
        return parts[0], body_remainder

    def _header_as_dict(self, header: str) -> dict[str, str]:
        """
        Preprocess each of the lines in the header, splitting on the
        colon, returning key-value pairs of unprocessed header fields.

        Since values are heterogeneous, don't do any processing here,
        but keys can be preprocessed into a canonical form
        """
        lines = header.split("\n")
        meta = {}
        for line in lines:
            # remove asterisks around keys
            line = line.strip()
            line = re.sub(r"^\*\*(.*?:)\*\*", r"\1", line)

            # split on first occurrence of non-url colon
            line_split = re.split(r"(?<!/):", line, 1)
            if len(line_split) == 1:
                # not a field (eg blank, etc.)
                continue

            # keeping in expanded form rather than a dict comprehension for now
            # in case any additional preprocessing needed.
            # strip trailing/leading whitespace
            line_split = [line.strip() for line in line_split]
            key, val = line_split
            # put key in canonical form
            key = key.lower().replace(" ", "_")

            meta[key] = val
        return meta

    def _combine_reviewers(self, meta: dict) -> dict:
        """
        Combine reviewer_1, reviewer_2, ... to a single reviewers field
        """
        if "reviewers" not in meta:
            meta["reviewers"] = []

        # first gather reviewers (don't mutate object we're iterating over)
        delete_keys = []
        for key, val in meta.items():
            if key.startswith("reviewer") and key != "reviewers":
                meta["reviewers"].append(val)
                delete_keys.append(key)

        meta = {k: v for k, v in meta.items() if k not in delete_keys}

        # later processing steps expect this to be a comma separated list
        # this is a string if we only specified the `reviewers` key in the review issue,
        # but a list if we specified `reviewer_1:` etc.
        if isinstance(meta["reviewers"], list):
            meta["reviewers"] = ", ".join(meta["reviewers"])

        return meta

    def _add_issue_metadata(
        self, meta: dict, issue: Issue, keys: list[str]
    ) -> dict:
        """
        Add keys from the review issue to the review model
        """
        for key in keys:
            meta[key] = getattr(issue, key)
        return meta

    def _preprocess_meta(self, meta: dict) -> dict:
        """
        Apply preprocessing steps before parsing specific fields in issue meta
        """
        meta = self._combine_reviewers(meta)
        # add other preprocessing steps here...
        return meta

    def _postprocess_meta(self, meta: dict, body: List[str]) -> dict:
        """
        Apply postprocessing steps after parsing individual fields.

        Putting all in one method for now, but individual steps should be split
        out for testing and maintainability if this gets too big ;)
        """
        meta = clean_date_accepted_key(meta)
        meta["issue_link"] = str(meta.get("url", "")).replace(
            "https://api.github.com/repos/", "https://github.com/"
        )
        # Get categories and issue review link
        meta["categories"] = self.get_categories(body, "## Scope", 10)
        # NOTE: right now the numeric value is hard coded based on the
        # number of categories listed in the issue template.
        # this could be made more flexible if it just runs until it runs
        # out of categories to parse
        meta["partners"] = self.get_categories(
            body, "## Community Partnerships", 3, keyed=True
        )
        if "joss_doi" in meta:
            # Normalize the JOSS archive field. Some issues use `JOSS DOI` others `JOSS`
            meta["joss"] = meta.pop("joss_doi")

        return meta

    def _postprocess_labels(self, meta: dict) -> dict:
        """
        Process specific labels for attributes in the review model.

        Presently, this method only checks if the review has the "archived"
        (LabelType.ARCHIVED) label and sets the active attribute to False
        if it does. We may add more label processing in the future.

        The intention behind this is to assign specific ReviewModel attributes
        based on the presence of certain labels in the review issue.
        """

        def _is_archived(label: str | Labels) -> bool:
            """Internal helper to check if a label is the "archived" label"""
            if isinstance(label, Labels):
                return label.type == LabelType.ARCHIVED
            return "archived" in label.lower()

        # Check if the review has the "archived" label
        if "labels" in meta and [
            label for label in meta["labels"] if _is_archived(label)
        ]:
            meta["active"] = False
        return meta

    def _parse_field(self, key: str, val: str) -> Any:
        """
        Method dispatcher for parsing specific header fields.
        If none found, return value unchanged.
        """
        if self._is_review_role(key):
            return self.get_contributor_data(val)
        # elif False:
        # add other conditions here for special processing of fields..
        #   pass
        else:
            return val

    def parse_issue(self, issue: Issue | str) -> ReviewModel:
        """
        Parse a single review header for its metadata

        issue : :class:`.Issue`
            The issue to parse! if a string, assume we are getting the issue body,
            which prevents us from doing some postprocessing steps
        """
        if isinstance(issue, Issue):
            issue_body = issue.body
        else:
            # issue body is passed in as string
            issue_body = issue

        # Separate the issue's header from its body
        header, body = self._split_header(issue_body)
        body = [line.strip() for line in body.split("\n")]

        # Process the header...
        meta = self._header_as_dict(header)
        meta = self._preprocess_meta(meta)

        model = {}
        for key, val in meta.items():
            model[key] = self._parse_field(key, val)

        # Add any requested metadata from the Issue object to the review object
        if isinstance(issue, Issue):
            model = self._add_issue_metadata(
                model,
                issue,
                [
                    "url",
                    "created_at",
                    "updated_at",
                    "closed_at",
                    "repository_url",
                    "labels",
                ],
            )

        # Finalize & cleanup review model before casting
        model = self._postprocess_meta(model, body)
        model = self._postprocess_labels(model)

        return ReviewModel(**model)

    def parse_issues(
        self, issues: list[Issue]
    ) -> tuple[dict[str, ReviewModel], dict[str, str]]:
        """Parses through each header comment for selected reviews and returns
        review metadata.

        Parameters
        ----------
        issues : list[:class:`.Issue`]
            List returned from the get_issues method that contains the
            metadata at the top of each issue

        Returns
        -------
        Dict
            A dictionary containing metadata for the issue including the
            package name, description, review team, version submitted etc.
            See meta_dates below for the full list of keys.
        """

        reviews = {}
        errors = {}
        for issue in tqdm(issues, desc="Processing reviews"):
            tqdm.write(f"Processing review {issue.title}")
            with logging_redirect_tqdm():
                try:
                    review = self.parse_issue(issue)
                    reviews[review.package_name] = review
                except ValidationError as e:
                    logger.error(
                        f"Error processing review {issue.title}. Skipping this review.",
                        exc_info=True,
                    )
                    errors[str(issue.url)] = "\n".join(
                        traceback.format_exception(e)
                    )

        return reviews, errors

    def get_contributor_data(
        self, line: str
    ) -> Union[ReviewUser, List[ReviewUser]]:
        """Parse names for various review roles from issue metadata.

        Parameters
        ----------
        line : list of str
            A single list item representing a single line in the issue
            containing metadata for the review.

        Returns
        -------
        dict
            Containing the metadata for a submitting author, reviewer, or
            maintainer(s).
        """
        users = line.split(",")
        models = [parse_user_names(username=user) for user in users]
        models = [model for model in models if model is not None]
        if len(models) == 1:
            models = models[0]
        return models

    # TODO: This now returns a dict of owner:repo_name to support graphql
    def get_repo_paths(
        self, review_issues: dict[str, ReviewModel]
    ) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of repository owner and names for each package.

        Currently we don't have API access setup for gitlab. So skip if
        url contains gitlab

        Parameters
        ----------
        review_issues : dict
            Dictionary containing all of the review issue paths.

        Returns
        -------
        dict
            Containing pkg_name: {owner: repo} for each review.
        """

        all_repos = {}
        for a_package in review_issues.keys():
            repo_url = review_issues[a_package].repository_link
            # for now skip if it's a gitlab repo
            if "gitlab" in repo_url:
                continue
            owner, repo = (
                repo_url.replace("https://github.com/", "")
                .replace("https://www.github.com/", "")
                .rstrip("/")
                .split("/", 1)
            )

            all_repos[a_package] = {"owner": owner, "repo_name": repo}
        return all_repos

    def get_categories(
        self,
        issue_list: list[str],
        section_str: str,
        num_vals: int,
        keyed: bool = False,
    ) -> list[str] | None:
        """Parse through a pyOS review issue and grab categories associated
        with a package

        Parameters
        ----------
        issue_list : list[list[str]]
            The body of the comment from the issue split into lines

        section_str : str
            The section string to find where the categories live in the review
            metadata. Example ## Scope contains the package categories such as
            data viz, etc

        num_vals : int
            Number of categories expected in the list. for instance
            3 partner options.

        keyed : bool
            If True, treat the category value as a key-value pair separated by a colon
            (and just extract the key).

            eg. ``- [x] Astropy: some other text`` would be parsed as ``'astropy'``
        """
        # Find the starting index of the category section
        index = [
            i for i, sublist in enumerate(issue_list) if section_str in sublist
        ]
        if len(index) == 0:
            logger.warning(f"{section_str} not found in the list")
            return None
        index = index[0]

        # find the list within the category
        cat_index = None
        for i in range(index + 1, len(issue_list)):
            if issue_list[i] and "- [" in issue_list[i]:
                cat_index = i
                break
        if cat_index is None:
            logger.warning(f"List not found for section {section_str}")
            return None

        # Get checked categories for package
        # TODO: it would be nice to figure out where the end of the list is
        # rather than hard coding it
        cat_list = issue_list[cat_index : cat_index + num_vals]
        selected = [
            item for item in cat_list if re.search(r"- \[[xX]\] ", item)
        ]
        # Above returns a list of list elements that are checked
        # Now, clean the extra markdown and only return the category text
        cleaned = [re.sub(r"- \[[xX]\] ", "", item) for item in selected]
        categories = [
            re.sub(r"(\w+) (\w+)", r"\1-\2", item) for item in cleaned
        ]
        categories = [item.lower().replace("[^1]", "") for item in categories]
        if keyed:
            categories = [
                KEYED_STRING.search(c).groupdict().get("key")
                for c in categories
                if KEYED_STRING.search(c) is not None
            ]

        return categories
