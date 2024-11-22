from pathlib import Path
from typing import Callable, Literal, Optional, Union, overload

import pytest

from pyosmeta.contributors import ProcessContributors
from pyosmeta.github_api import GitHubAPI
from pyosmeta.models.github import Issue
from pyosmeta.parse_issues import ProcessIssues

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def ghuser_response():
    """This is the initial GitHub response. I changed the username to
    create this object"""
    expected_response = {
        "login": "chayadecacao",
        "id": 123456,
        "node_id": "MDQ6VXNlcjU3ODU0Mw==",
        "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/cacao",
        "html_url": "https://github.com/cacao",
    }
    return expected_response


@pytest.fixture
def mock_github_api(mocker, ghuser_response):
    mock_api = mocker.Mock(spec=GitHubAPI)
    mock_api.get_user_info.return_value = ghuser_response
    return mock_api


@pytest.fixture
def process_contribs(contrib_github_api):
    """A fixture that creates a"""
    return ProcessContributors(contrib_github_api)


@pytest.fixture
def github_api():
    """A fixture that instantiates an instance of the GitHubAPI object"""
    return GitHubAPI(
        org="pyopensci", repo="pyosmeta", labels=["label1", "label2"]
    )


@pytest.fixture
def process_issues():
    """A fixture that returns an instance of the ProcessIssues class"""
    gh_client = GitHubAPI()
    process_issues = ProcessIssues(gh_client)
    return process_issues


@pytest.fixture
def issue_list():
    """A fixture representing an API return from GitHub for a two issues
    to be used in our test suite.

    We only use the body for parse_issues but for now i'll leave it all
    as it may be useful for other tests.
    """
    issue = [
        Issue(
            **{
                "url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/147",
                "repository_url": "https://api.github.com/repos/pyOpenSci/software-submission",
                "labels_url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/147/labels{/name}",
                "number": 147,
                "title": "`sunpy` Review",
                "assignee": {
                    "login": "cmarmo",
                    "id": 1662261,
                    "node_id": "MDQ6VXNlcjE2NjIyNjE=",
                    "avatar_url": "https://avatars.githubusercontent.com/u/1662261?v=4",
                    "type": "User",
                    "site_admin": False,
                },
                "assignees": [],
                "milestone": None,
                "comments": 35,
                "created_at": "2023-10-30T18:45:06Z",
                "updated_at": "2024-02-22T01:24:31Z",
                "closed_at": "2024-01-27T23:05:39Z",
                "author_association": "NONE",
                "active_lock_reason": None,
                "body": "Submitting Author: Nabil Freij (@nabobalis)\r\nAll current maintainers: @ehsteve,@dpshelio,@wafels,@ayshih,@Cadair,@nabobalis,@dstansby,@DanRyanIrish,@wtbarnes,@ConorMacBride,@alasdairwilson,@hayesla,@vn-ki\r\nPackage Name: sunpy\r\nOne-Line Description of Package: Python for Solar Physics \r\nRepository Link: https://github.com/sunpy/sunpy\r\nVersion submitted: 5.0.1\r\nEditor: @cmarmo \r\nReviewer 1: @Septaris\r\nReviewer 2: @nutjob4life\r\nArchive: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8384174.svg)](https://doi.org/10.5281/zenodo.8384174)\r\nVersion accepted: 5.1.1\r\nJOSS DOI: [![DOI](https://joss.theoj.org/papers/10.21105/joss.01832/status.svg)](https://joss.theoj.org/papers/10.21105/joss.01832)\r\nDate accepted (month/day/year): 01/18/2024\r\n\r\n---\r\n\r\n## Code of Conduct & Commitment to Maintain Package\r\n\r\n- [X] I agree to abide by [pyOpenSci's Code of Conduct][PyOpenSciCodeOfConduct] during the review process and in maintaining my package after should it be accepted.\r\n- [X] I have read and will commit to package maintenance after the review as per the [pyOpenSci Policies Guidelines][Commitment].\r\n\r\n## Description\r\n\r\n- sunpy is a community-developed, free and open-source solar data analysis environment for Python. It includes an interface for searching and downloading data from multiple data providers, data containers for image and time series data, commonly used solar coordinate frames and associated transformations, as well as other functionality needed for solar data analysis.\r\n\r\n## Scope\r\n\r\n- Please indicate which category or categories. \r\nCheck out our [package scope page][PackageCategories] to learn more about our \r\nscope. (If you are unsure of which category you fit, we suggest you make a pre-submission inquiry):\r\n\r\n\t- [X] Data retrieval\r\n\t- [X] Data extraction\r\n\t- [X] Data processing/munging\r\n\t- [ ] Data deposition\r\n\t- [ ] Data validation and testing\r\n\t- [X] Data visualization[^1]\t  \r\n\t- [ ] Workflow automation\r\n\t- [ ] Citation management and bibliometrics\r\n\t- [ ] Scientific software wrappers\r\n\t- [ ] Database interoperability\r\n\r\n## Domain Specific\r\n\r\n- [ ] Geospatial\r\n- [ ] Education\r\n\t\r\n## Community Partnerships\r\nIf your package is associated with a pyOpenSci partner community, please check below:\r\n\r\n- [ ] astropy\r\n- [x] sunpy\r\n- [ ] [Pangeo][pangeoWebsite]\r\n\t- [ ] My package adheres to the [Pangeo standards listed in the pyOpenSci peer review guidebook][PangeoCollaboration]\r\n\r\n## Technical checks\r\n\r\nFor details about the pyOpenSci packaging requirements, see our [packaging guide][PackagingGuide]. Confirm each of the following by checking the box. This package:\r\n\r\n- [X] does not violate the Terms of Service of any service it interacts with. \r\n- [X] uses an [OSI approved license][OsiApprovedLicense].\r\n- [X] contains a README with instructions for installing the development version. \r\n- [ ] includes documentation with examples for all functions.\r\n  **I will need to double check the examples, we have documentation for all public API**\r\n- [X] contains a tutorial with examples of its essential functions and uses.\r\n- [X] has a test suite.\r\n- [X] has continuous integration setup, such as GitHub Actions CircleCI, and/or others.\r\n\r\n## Are you OK with Reviewers Submitting Issues and/or pull requests to your Repo Directly?\r\nThis option will allow reviewers to open smaller issues that can then be linked to PR's rather than submitting a more dense text based review. It will also allow you to demonstrate addressing the issue via PR links.\r\n\r\n- [x] Yes I am OK with reviewers submitting requested changes as issues to my repo. Reviewers will then link to the issues in their submitted review.\r\n\r\nConfirm each of the following by checking the box.\r\n\r\n- [X] I have read the [author guide](https://www.pyopensci.org/software-peer-review/how-to/author-guide.html). \r\n- [X] I expect to maintain this package for at least 2 years and can help find a replacement for the maintainer (team) if needed.\r\n\r\n## Please fill out our survey\r\n\r\n- [X] [Last but not least please fill out our pre-review survey](https://forms.gle/F9mou7S3jhe8DMJ16). This helps us track\r\nsubmission and improve our peer review process. We will also ask our reviewers \r\nand editors to fill this out.\r\n\r\n**P.S.** Have feedback/comments about our review process? Leave a comment [here][Comments]\r\n\r\n## Editor and Review Templates\r\n\r\nThe [editor template can be found here][Editor Template].\r\n\r\nThe [review template can be found here][Review Template].\r\n\r\n[PackagingGuide]: https://www.pyopensci.org/python-package-guide/\r\n\r\n[PackageCategories]: https://www.pyopensci.org/software-peer-review/about/package-scope.html\r\n\r\n[JournalOfOpenSourceSoftware]: http://joss.theoj.org/\r\n\r\n[JossSubmissionRequirements]: https://joss.readthedocs.io/en/latest/submitting.html#submission-requirements\r\n\r\n[JossPaperRequirements]: https://joss.readthedocs.io/en/latest/submitting.html#what-should-my-paper-contain\r\n\r\n[PyOpenSciCodeOfConduct]: https://www.pyopensci.org/governance/CODE_OF_CONDUCT\r\n\r\n[OsiApprovedLicense]: https://opensource.org/licenses\r\n\r\n[Editor Template]: https://www.pyopensci.org/software-peer-review/appendices/templates.html#editor-s-template\r\n\r\n[Review Template]: https://www.pyopensci.org/software-peer-review/appendices/templates.html#peer-review-template\r\n\r\n[Comments]: https://pyopensci.discourse.group/\r\n\r\n[PangeoCollaboration]: https://www.pyopensci.org/software-peer-review/partners/pangeo\r\n\r\n[pangeoWebsite]: https://www.pangeo.io\r\n[Commitment]: https://www.pyopensci.org/software-peer-review/our-process/policies.html#after-acceptance-package-ownership-and-maintenance\r\n\r\n",
                "state_reason": "completed",
            }
        ),
        Issue(
            **{
                "url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/146",
                "repository_url": "https://api.github.com/repos/pyOpenSci/software-submission",
                "title": "ncompare",
                "number": 147,
                "user": {
                    "login": "danielfromearth",
                    "id": 114174502,
                    "node_id": "U_kgDOBs4qJg",
                    "avatar_url": "https://avatars.githubusercontent.com/u/114174502?v=4",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/danielfromearth",
                    "received_events_url": "https://api.github.com/users/danielfromearth/received_events",
                    "type": "User",
                    "site_admin": False,
                },
                "labels": [],
                "state": "open",
                "locked": False,
                "assignee": {
                    "login": "tomalrussell",
                    "id": 2762769,
                    "type": "User",
                    "site_admin": False,
                },
                "assignees": [],
                "milestone": None,
                "comments": 21,
                "created_at": "2023-10-25T13:12:48Z",
                "updated_at": "2024-02-06T17:59:37Z",
                "closed_at": None,
                "author_association": "NONE",
                "active_lock_reason": None,
                "body": 'Submitting Author: Daniel Kaufman (@danielfromearth)\r\nAll current maintainers: (@danielfromearth)\r\nPackage Name: `ncompare`\r\nOne-Line Description of Package: `ncompare` compares two netCDF files at the command line, by generating a report of the matching and non-matching groups, variables, and attributes.\r\nRepository Link:  https://github.com/nasa/ncompare\r\nVersion submitted:   1.4.0\r\nEditor: @tomalrussell   \r\nReviewer 1: @cmarmo   \r\nReviewer 2: @cmtso  \r\nArchive: [10.5281/zenodo.10625407](https://zenodo.org/doi/10.5281/zenodo.10625407)\r\nJOSS DOI: TBD\r\nVersion accepted: 1.7.2\r\nDate accepted (month/day/year): 02/06/2024\r\n\r\n---\r\n\r\n## Code of Conduct & Commitment to Maintain Package\r\n\r\n- [x] I agree to abide by [pyOpenSci\'s Code of Conduct][PyOpenSciCodeOfConduct] during the review process and in maintaining my package after should it be accepted.\r\n- [x] I have read and will commit to package maintenance after the review as per the [pyOpenSci Policies Guidelines][Commitment].\r\n\r\n## Description\r\n\r\nThis tool ("ncompare") compares the structure of two Network Common Data Form (NetCDF) files at the command line. \r\n\r\n\r\n## Scope\r\n\r\n- Please indicate which category or categories. \r\nCheck out our [package scope page][PackageCategories] to learn more about our \r\nscope. (If you are unsure of which category you fit, we suggest you make a pre-submission inquiry):\r\n\r\n\t- [ ] Data retrieval\r\n\t- [ ] Data extraction\r\n\t- [ ] Data processing/munging\r\n\t- [ ] Data deposition\r\n\t- [x] Data validation and testing\r\n\t- [ ] Data visualization[^1]\r\n\t- [ ] Workflow automation\r\n\t- [ ] Citation management and bibliometrics\r\n\t- [ ] Scientific software wrappers\r\n\t- [ ] Database interoperability\r\n\r\nDomain Specific & Community Partnerships \r\n\r\n\t- [ ] Geospatial\r\n\t- [ ] Education\r\n\t- [ ] Pangeo\r\n\t\r\n\r\n## Community Partnerships\r\nIf your package is associated with an \r\nexisting community please check below:\r\n\r\n- [ ] [Pangeo][pangeoWebsite]\r\n\t- [ ] My package adheres to the [Pangeo standards listed in the pyOpenSci peer review guidebook][PangeoCollaboration]\r\n\r\n> [^1]: Please fill out a pre-submission inquiry before submitting a data visualization package.\r\n\r\n- **For all submissions**, explain how the and why the package falls under the categories you indicated above. In your explanation, please address the following points (briefly, 1-2 sentences for each):  \r\n\r\n  - Who is the target audience and what are scientific applications of this package?\r\n  \r\nThe target audience is anyone who manages the generation, manipulation, or validation of netCDF files. This package can be applied to to these netCDF file tasks in any scientific discipline;\xa0although it would be most relevant to applications with large multidimensional datasets, e.g., for comparing climate models, for Earth science data reanalyses, and for remote sensing data.\r\n\r\n  - Are there other Python packages that accomplish the same thing? If so, how does yours differ?\r\n\r\nThe `ncdiff` function in the `nco` (netCDF Operators) library, as well as `ncmpidiff` and `nccmp`, compute value \r\ndifferences, but --- as far as we are aware --- do not have a dedicated function to show structural differences between netCDF4 datasets.  Our package, `ncompare` provides a light-weight Python-based tool for rapid **visual** comparisons of group & variable _structures_, _attributes_, and _chunking_.  \r\n\r\n  - If you made a pre-submission enquiry, please paste the link to the corresponding issue, forum post, or other discussion, or `@tag` the editor you contacted:\r\n\r\nPre-submission inquiry #142 \r\n\r\n## Technical checks\r\n\r\nFor details about the pyOpenSci packaging requirements, see our [packaging guide][PackagingGuide]. Confirm each of the following by checking the box. This package:\r\n\r\n- [x] does not violate the Terms of Service of any service it interacts with. \r\n- [x] uses an [OSI approved license][OsiApprovedLicense].\r\n- [x] contains a README with instructions for installing the development version. \r\n- [x] includes documentation with examples for all functions.\r\n- [x] contains a tutorial with examples of its essential functions and uses.\r\n- [x] has a test suite.\r\n- [x] has continuous integration setup, such as GitHub Actions CircleCI, and/or others.\r\n\r\n## Publication Options\r\n\r\n- [x] Do you wish to automatically submit to the [Journal of Open Source Software][JournalOfOpenSourceSoftware]? If so:\r\n\r\n<details>\r\n <summary>JOSS Checks</summary>  \r\n\r\n- [x] The package has an **obvious research application** according to JOSS\'s definition in their [submission requirements][JossSubmissionRequirements]. Be aware that completing the pyOpenSci review process **does not** guarantee acceptance to JOSS. Be sure to read their submission requirements (linked above) if you are interested in submitting to JOSS.\r\n- [x] The package is not a "minor utility" as defined by JOSS\'s [submission requirements][JossSubmissionRequirements]: "Minor ‘utility’ packages, including ‘thin’ API clients, are not acceptable." pyOpenSci welcomes these packages under "Data Retrieval", but JOSS has slightly different criteria.\r\n- [(NOT YET)] The package contains a `paper.md` matching [JOSS\'s requirements][JossPaperRequirements] with a high-level description in the package root or in `inst/`.\r\n- [(NOT YET)] The package is deposited in a long-term repository with the DOI: \r\n\r\n*Note: JOSS accepts our review as theirs. You will NOT need to go through another full review. JOSS will only review your paper.md file. Be sure to link to this pyOpenSci issue when a JOSS issue is opened for your package. Also be sure to tell the JOSS editor that this is a pyOpenSci reviewed package once you reach this step.*\r\n  \r\n</details>\r\n\r\n## Are you OK with Reviewers Submitting Issues and/or pull requests to your Repo Directly?\r\nThis option will allow reviewers to open smaller issues that can then be linked to PR\'s rather than submitting a more dense text based review. It will also allow you to demonstrate addressing the issue via PR links.\r\n\r\n- [x] Yes I am OK with reviewers submitting requested changes as issues to my repo. Reviewers will then link to the issues in their submitted review.\r\n\r\nConfirm each of the following by checking the box.\r\n\r\n- [x] I have read the [author guide](https://www.pyopensci.org/software-peer-review/how-to/author-guide.html). \r\n- [x] I expect to maintain this package for at least 2 years and can help find a replacement for the maintainer (team) if needed.\r\n\r\n## Please fill out our survey\r\n\r\n- [x] [Last but not least please fill out our pre-review survey](https://forms.gle/F9mou7S3jhe8DMJ16). This helps us track\r\nsubmission and improve our peer review process. We will also ask our reviewers \r\nand editors to fill this out.\r\n\r\n**P.S.** Have feedback/comments about our review process? Leave a comment [here][Comments]\r\n\r\n## Editor and Review Templates\r\n\r\nThe [editor template can be found here][Editor Template].\r\n\r\nThe [review template can be found here][Review Template].\r\n\r\n[PackagingGuide]: https://www.pyopensci.org/python-package-guide/\r\n\r\n[PackageCategories]: https://www.pyopensci.org/software-peer-review/about/package-scope.html\r\n\r\n[JournalOfOpenSourceSoftware]: http://joss.theoj.org/\r\n\r\n[JossSubmissionRequirements]: https://joss.readthedocs.io/en/latest/submitting.html#submission-requirements\r\n\r\n[JossPaperRequirements]: https://joss.readthedocs.io/en/latest/submitting.html#what-should-my-paper-contain\r\n\r\n[PyOpenSciCodeOfConduct]: https://www.pyopensci.org/governance/CODE_OF_CONDUCT\r\n\r\n[OsiApprovedLicense]: https://opensource.org/licenses\r\n\r\n[Editor Template]: https://www.pyopensci.org/software-peer-review/appendices/templates.html#editor-s-template\r\n\r\n[Review Template]: https://www.pyopensci.org/software-peer-review/appendices/templates.html#peer-review-template\r\n\r\n[Comments]: https://pyopensci.discourse.group/\r\n\r\n[PangeoCollaboration]: https://www.pyopensci.org/software-peer-review/partners/pangeo\r\n\r\n[pangeoWebsite]: https://www.pangeo.io\r\n[Commitment]: https://www.pyopensci.org/software-peer-review/our-process/policies.html#after-acceptance-package-ownership-and-maintenance\r\n',
                "reactions": {
                    "url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/146/reactions",
                    "total_count": 0,
                },
                "timeline_url": "https://api.github.com/repos/pyOpenSci/software-submission/issues/146/timeline",
                "performed_via_github_app": None,
                "state_reason": None,
            }
        ),
    ]
    return issue


@pytest.fixture
def data_file() -> Callable[[Optional[str], bool], Union[str, Path]]:
    """
    Closure that returns a getter for files within the data directory.

    Examples:

        >>> data_file()
        DATA_DIR
        >>> data_file('myfile.txt')
        DATA_DIR / 'myfile.txt'
        >>> data_file('myfile.txt', load=True)
        {contents of myfile.txt}
    """

    @overload
    def _data_file(file: Optional[str], load: Literal[True]) -> str: ...
    @overload
    def _data_file(file: Optional[str], load: Literal[False]) -> Path: ...

    def _data_file(
        file: Optional[str] = None, load: bool = False
    ) -> Union[str, Path]:
        if file is None:
            return DATA_DIR

        path = DATA_DIR / file
        if load:
            with open(path, "r") as a_file:
                data = a_file.read()
            return data
        else:
            return path

    return _data_file
