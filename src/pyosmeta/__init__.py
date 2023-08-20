from .contributors import PersonModel, ProcessContributors
from .parse_issues import ProcessIssues, ReviewModel

# Trick suggested by flake8 maintainer to ensure the imports above don't
# get flagged as being "unused"
__all__ = (
    "ProcessIssues",
    "ReviewModel",
    "PersonModel",
    "ProcessContributors",
)

try:
    from ._version_generated import __version__
except ImportError:
    __version__ = "unreleased"
