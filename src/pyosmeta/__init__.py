from .contributors import ProcessContributors
from .models import PersonModel, ReviewModel
from .parse_issues import ProcessIssues

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
