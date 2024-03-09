from pyosmeta.models import ReviewModel

# We could setup some example data using fixtures and a conf.py
# Once we have a better view of the test suite.
example = {
    "submitting_author": {
        "github_username": "nabobalis",
        "name": "Nabil Freij",
    },
    "all_current_maintainers": [],
    "package_name": "sunpy",
    "one-line_description_of_package": "Python for Solar Physics",
    "repository_link": "https://github.com/sunpy/sunpy",
    "version_submitted": "5.0.1",
    "editor": {"github_username": "cmarmo", "name": ""},
    "reviewer_1": {"github_username": "Septaris", "name": ""},
    "reviewer_2": {"github_username": "nutjob4life", "name": ""},
    "archive": "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8384174.svg)](https://doi.org/10.5281/zenodo.8384174)",
    "version_accepted": "5.1.1",
    "joss_doi": "[![DOI](https://joss.theoj.org/papers/10.21105/joss.01832/status.svg)](https://joss.theoj.org/papers/10.21105/joss.01832)",
    "date_accepted": "01/18/2024",
    "categories": [
        "data-retrieval",
        "data-extraction",
        "data-processing/munging",
        "data-visualization",
    ],
}


def test_alias_choices_validation():
    """Test that model correctly recognizes the field alias"""

    new = ReviewModel(**example)
    assert new.date_accepted == "2024-01-18"
    assert new.package_description == "Python for Solar Physics"
