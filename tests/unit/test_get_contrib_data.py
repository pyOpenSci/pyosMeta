import pytest
from pydantic import ValidationError

from pyosmeta.models.github import Issue

sample_response = {
    "url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/147",
    "repository_url": "https://api.github.com/repos/pyOpenSci/software-submission",
    "title": "`sunpy` Review",
    "number": 147,
    "assignee": {"login": "cmarmo", "id": 12345, "type": "User"},
    "comments": 35,
    "created_at": "2023-10-30T18:45:06Z",
    "updated_at": "2024-02-22T01:24:31Z",
    "closed_at": "2024-01-27T23:05:39Z",
    "author_association": "NONE",
    "active_lock_reason": None,
    "body": "Submitting Author: Nabil Freij (@nabobalis)\r\nAll current maintainers: @ehsteve,@dpshelio,@wafels,@ayshih,@Cadair,@nabobalis,@dstansby,@DanRyanIrish,@wtbarnes,@ConorMacBride,@alasdairwilson,@hayesla,@vn-ki\r\nPackage Name: sunpy\r\nOne-Line Description of Package: Python for Solar Physics \r\nRepository Link: https://github.com/sunpy/sunpy\r\nVersion submitted: 5.0.1\r\nEditor: @cmarmo \r\nReviewer 1: @Septaris\r\nReviewer 2: @nutjob4life\r\nArchive: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8384174.svg)](https://doi.org/10.5281/zenodo.8384174)\r\nVersion accepted: 5.1.1\r\nJOSS DOI: [![DOI](https://joss.theoj.org/papers/10.21105/joss.01832/status.svg)](https://joss.theoj.org/papers/10.21105/joss.01832)\r\nDate accepted (month/day/year): 01/18/2024\r\n\r\n---\r\n\r\n## Code of Conduct & Commitment to Maintain Package\r\n\r\n- [X] I agree to abide by [pyOpenSci's Code of Conduct][PyOpenSciCodeOfConduct] during the review process and in maintaining my package after should it be accepted.\r\n- [X] I have read and will commit to package maintenance after the review as per the [pyOpenSci Policies Guidelines][Commitment].\r\n\r\n## Description\r\n\r\n- sunpy is a community-developed, free and open-source solar data analysis environment for Python. It includes an interface for searching and downloading data from multiple data providers, data containers for image and time series data, commonly used solar coordinate frames and associated transformations, as well as other functionality needed for solar data analysis.\r\n\r\n## Scope\r\n\r\n- Please indicate which category or categories. \r\nCheck out our [package scope page][PackageCategories] to learn more about our \r\nscope. (If you are unsure of which category you fit, we suggest you make a pre-submission inquiry):\r\n\r\n\t- [X] Data retrieval\r\n\t- [X] Data extraction\r\n\t- [X] Data processing/munging\r\n\t- [ ] Data deposition\r\n\t- [ ] Data validation and testing\r\n\t- [X] Data visualization[^1]\t  \r\n\t- [ ] Workflow automation\r\n\t- [ ] Citation management and bibliometrics\r\n\t- [ ] Scientific software wrappers\r\n\t- [ ] Database interoperability\r\n\r\n## Domain Specific\r\n\r\n- [ ] Geospatial\r\n- [ ] Education\r\n\t\r\n## Community Partnerships\r\nIf your package is associated with a pyOpenSci partner community, please check below:\r\n\r\n- [ ] astropy\r\n- [x] sunpy\r\n- [ ] [Pangeo][pangeoWebsite]\r\n\t- [ ] My package adheres to the [Pangeo standards listed in the pyOpenSci peer review guidebook][PangeoCollaboration]\r\n\r\n## Technical checks\r\n\r\nFor details about the pyOpenSci packaging requirements, see our [packaging guide][PackagingGuide]. Confirm each of the following by checking the box. This package:\r\n\r\n- [X] does not violate the Terms of Service of any service it interacts with. \r\n- [X] uses an [OSI approved license][OsiApprovedLicense].\r\n- [X] contains a README with instructions for installing the development version. \r\n- [ ] includes documentation with examples for all functions.\r\n  **I will need to double check the examples, we have documentation for all public API**\r\n- [X] contains a tutorial with examples of its essential functions and uses.\r\n- [X] has a test suite.\r\n- [X] has continuous integration setup, such as GitHub Actions CircleCI, and/or others.\r\n\r\n## Are you OK with Reviewers Submitting Issues and/or pull requests to your Repo Directly?\r\nThis option will allow reviewers to open smaller issues that can then be linked to PR's rather than submitting a more dense text based review. It will also allow you to demonstrate addressing the issue via PR links.\r\n\r\n- [x] Yes I am OK with reviewers submitting requested changes as issues to my repo. Reviewers will then link to the issues in their submitted review.\r\n\r\nConfirm each of the following by checking the box.\r\n\r\n- [X] I have read the [author guide](https://www.pyopensci.org/software-peer-review/how-to/author-guide.html). \r\n- [X] I expect to maintain this package for at least 2 years and can help find a replacement for the maintainer (team) if needed.\r\n\r\n## Please fill out our survey\r\n\r\n- [X] [Last but not least please fill out our pre-review survey](https://forms.gle/F9mou7S3jhe8DMJ16). This helps us track\r\nsubmission and improve our peer review process. We will also ask our reviewers \r\nand editors to fill this out.\r\n\r\n**P.S.** Have feedback/comments about our review process? Leave a comment [here][Comments]\r\n\r\n## Editor and Review Templates\r\n\r\nThe [editor template can be found here][Editor Template].\r\n\r\nThe [review template can be found here][Review Template].\r\n\r\n[PackagingGuide]: https://www.pyopensci.org/python-package-guide/\r\n\r\n[PackageCategories]: https://www.pyopensci.org/software-peer-review/about/package-scope.html\r\n\r\n[JournalOfOpenSourceSoftware]: http://joss.theoj.org/\r\n\r\n[JossSubmissionRequirements]: https://joss.readthedocs.io/en/latest/submitting.html#submission-requirements\r\n\r\n[JossPaperRequirements]: https://joss.readthedocs.io/en/latest/submitting.html#what-should-my-paper-contain\r\n\r\n[PyOpenSciCodeOfConduct]: https://www.pyopensci.org/governance/CODE_OF_CONDUCT\r\n\r\n[OsiApprovedLicense]: https://opensource.org/licenses\r\n\r\n[Editor Template]: https://www.pyopensci.org/software-peer-review/appendices/templates.html#editor-s-template\r\n\r\n[Review Template]: https://www.pyopensci.org/software-peer-review/appendices/templates.html#peer-review-template\r\n\r\n[Comments]: https://pyopensci.discourse.group/\r\n\r\n[PangeoCollaboration]: https://www.pyopensci.org/software-peer-review/partners/pangeo\r\n\r\n[pangeoWebsite]: https://www.pangeo.io\r\n[Commitment]: https://www.pyopensci.org/software-peer-review/our-process/policies.html#after-acceptance-package-ownership-and-maintenance\r\n\r\n## Comments from Nabil\r\n\r\n \r\n",
    "timeline_url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/147/timeline",
}

sample_response_no_name = {
    "comments": 35,
    "created_at": "2023-10-30T18:45:06Z",
    "author_association": "NONE",
    "active_lock_reason": None,
    "body": "Submitting Author: Nabil Freij (@nabobalis)\r\nAll current maintainers: @wtbarnes,@ConorMacBride,@alasdairwilson,@hayesla,@vn-ki\r\n\r\nOne-Line Description of Package: Python for Solar Physics \r\nn",
    "timeline_url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/147/timeline",
}


def test_parse_header_as_dict(process_issues):
    """Test that we can parse a header as a dict"""
    header, body = process_issues._split_header(sample_response["body"])

    meta = process_issues._header_as_dict(header)

    assert isinstance(meta, dict)


def test_comment_no_name(process_issues):
    """Test what happens if the package name key is missing in the review
    this means that a user has likely modified the template.

    In that case we just insert a placeholder name and keep processing issues.
    This is a template issue not a code issue.
    """

    with pytest.raises(ValidationError):
        _ = process_issues.parse_issue(Issue(**sample_response_no_name))


def test_comment_to_list_package_name(process_issues):
    """Test that comment_to_list returns a proper package name"""
    header, body = process_issues._split_header(sample_response["body"])

    meta = process_issues._header_as_dict(header)
    assert meta["package_name"] == "sunpy"

    review = process_issues.parse_issue(Issue(**sample_response))
    assert review.package_name == "sunpy"
