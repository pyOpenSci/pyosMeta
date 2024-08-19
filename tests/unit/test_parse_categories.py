import pytest

from pyosmeta.models import ReviewModel

checked = [
    "Submitting Author",
    "Nabil Freij (@nabobalis)",
    "- sunpy is a community-developed, free and open-source.",
    "## Scope",
    "- Please indicate which category or categories.",
    "- [X] Data retrieval",
    "- [ ] Data extraction",
    "- [x] Data Viz",
    "## Domain Specific",
    "something else",
]

not_checked = [
    "Submitting Author",
    "Nabil Freij (@nabobalis)",
    "- sunpy is a community-developed, free and open-source.",
    "## Scope",
    "- Please indicate which category or categories.",
    "- [ ] Data retrieval",
    "- [ ] Data extraction",
    "- [ ] Data Viz",
    "## Domain Specific",
    "something else",
]

no_categories = [
    "Submitting Author",
    "Nabil Freij (@nabobalis)",
    "- sunpy is a community-developed, free and open-source.",
    "something else",
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
    issue_list: list[list[str]],
    expected_categories: list[str | None],
    process_issues,
):
    # Call the get_categories method
    categories = process_issues.get_categories(issue_list, "## Scope", 3)

    # Assert the result matches the expected categories
    assert categories == expected_categories


@pytest.mark.parametrize(
    "input_categories,expected_return",
    [
        (
            ["data-processing"],
            ["data-processing-munging"],
        ),
        (
            ["data-processing/munging"],
            ["data-processing-munging"],
        ),
        (
            ["scientific-software and friends"],
            ["scientific-software-wrapper"],
        ),
        (
            ["data-validation and things -testing"],
            ["data-validation-testing"],
        ),
        (
            ["data-processing", "data-extraction"],
            ["data-processing-munging", "data-extraction"],
        ),
    ],
)
def test_clean_categories(
    input_categories: list[str], expected_return: list[str]
):
    """Test that ensures our pydantic model cleans categories as expected"""

    review = ReviewModel.clean_categories(categories=input_categories)
    assert review == expected_return


@pytest.mark.parametrize(
    "partners,input_file", [(["astropy"], "reviews/partnership_astropy.txt")]
)
def test_parse_partnerships(partners, input_file, data_file, process_issues):
    """
    The community partnership checkboxes should be correctly parsed into
    a value in the :class:`.Partnerships` enum
    """
    review = data_file(input_file, True)
    review = process_issues.parse_issue(review)
    assert review.partners == partners
