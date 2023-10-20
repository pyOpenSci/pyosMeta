from unittest import TestCase
from pyosmeta.parse_issues import parse_user_names


class TestParseUserNames(TestCase):
    def setUp(self) -> None:
        self.name1 = "Test User (@test1user)"
        self.name2 = "(@test2user)"
        self.name3 = "Test (user) 3 (@test3user)"
        self.name4 = "@test4user"

    def test_parse_1(self):
        d = {"name": "Test User", "github_username": "test1user"}
        self.assertDictEqual(d, parse_user_names(self.name1))

    def test_parse_2(self):
        d = {"name": "", "github_username": "test2user"}
        self.assertDictEqual(d, parse_user_names(self.name2))

    def test_parse_3(self):
        d = {"name": "Test user 3", "github_username": "test3user"}
        self.assertDictEqual(d, parse_user_names(self.name3))

    def test_parse_4(self):
        d = {"name": "", "github_username": "test4user"}
        self.assertDictEqual(d, parse_user_names(self.name4))
