"""Test parse issues workflow"""


def test_parse_issue_header(process_issues, issue_list):
    """Should return a dict, should return 2 keys in the dict"""

    reviews = process_issues.parse_issue_header(issue_list, 20)
    print(reviews)
    assert len(reviews.keys()) == 2
    assert list(reviews.keys())[0] == "sunpy"
