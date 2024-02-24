import pytest

from pyosmeta.parse_issues import ProcessIssues

checked = [
    ["Submitting Author", "Nabil Freij (@nabobalis)"],
    ["- sunpy is a community-developed, free and open-source."],
    ["## Scope"],
    ["- Please indicate which category or categories."],
    ["- [X] Data retrieval"],
    ["- [ ] Data extraction"],
    ["- [x] Data Viz"],
    ["## Domain Specific"],
    ["something else"],
]

not_checked = [
    ["Submitting Author", "Nabil Freij (@nabobalis)"],
    ["- sunpy is a community-developed, free and open-source."],
    ["## Scope"],
    ["- Please indicate which category or categories."],
    ["- [ ] Data retrieval"],
    ["- [ ] Data extraction"],
    ["- [ ] Data Viz"],
    ["## Domain Specific"],
    ["something else"],
]

no_categories = [
    ["Submitting Author", "Nabil Freij (@nabobalis)"],
    ["- sunpy is a community-developed, free and open-source."],
    ["something else"],
]


@pytest.mark.parametrize(
    "issue_list, expected_categories",
    [
        (
            checked,
            ["data-retrieval", "data-viz"],
        ),
        (
            not_checked,
            [],
        ),
        (
            no_categories,
            None,
        ),
    ],
)
def test_get_categories(
    issue_list: list[list[str]], expected_categories: list[str | None]
):
    # Initialize your class or use an existing instance
    issues = ProcessIssues(
        org="pyopensci",
        repo_name="software-submission",
        label_name="presubmission",
    )

    # Call the get_categories method
    categories = issues.get_categories(issue_list, "## Scope", 3)

    # Assert the result matches the expected categories
    assert categories == expected_categories
