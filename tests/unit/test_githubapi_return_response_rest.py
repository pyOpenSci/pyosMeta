import logging
from unittest.mock import Mock, patch

import pytest
import requests

from pyosmeta.github_api import GitHubAPI


class TestGitHubAPI:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up an instance of GitHubAPI before each test."""
        self.api = GitHubAPI()

        # Create default mock response
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1, "name": "repo1"}]
        mock_response.links = {}  # No pagination
        mock_response.status_code = 200
        mock_response.headers = {"X-RateLimit-Remaining": "10"}
        # Patch requests.get for all tests
        self.mock_get_patcher = patch(
            "requests.get", return_value=mock_response
        )
        self.mock_get = self.mock_get_patcher.start()

    def teardown_method(self):
        """Stop the patch after each test."""
        patch.stopall()

    def test_single_page_response(self):
        """Test a successful API response with a single page (no pagination)."""
        # print(self.mock_get.call_args)
        result = self.api._get_response_rest(
            "https://api.github.com/repos/test"
        )
        assert result == [{"id": 1, "name": "repo1"}]

    def test_multi_page_response(self):
        """Test handling multiple pages (pagination).
        This test is unusual because we setup a non paginated response
        in the setup method. So we have to stop that mock and restart it with
        new values for it to work properly.
        """
        # Make sure the setup mock doesn't propagate here
        self.mock_get.stop()
        # repatch requests.get with new mock behavior (paginated)
        self.mock_get = patch("requests.get").start()
        # Simulate pagination with multiple response Mocks
        self.mock_get.side_effect = [
            Mock(
                json=Mock(return_value=[{"id": 1, "name": "repo1"}]),
                links={
                    "next": {"url": "https://api.github.com/repos/test?page=2"}
                },
                status_code=200,
                headers={"X-RateLimit-Remaining": "10"},
            ),
            Mock(
                json=Mock(return_value=[{"id": 2, "name": "repo2"}]),
                links={},
                status_code=200,
                headers={"X-RateLimit-Remaining": "10"},
            ),
        ]

        result = self.api._get_response_rest(
            "https://api.github.com/repos/test"
        )
        assert result == [
            {"id": 1, "name": "repo1"},
            {"id": 2, "name": "repo2"},
        ]
        assert self.mock_get.call_count == 2

    @patch.object(GitHubAPI, "handle_rate_limit")
    def test_rate_limit_handling(self, mock_handle_rate_limit):
        """Test that rate limiting is handled correctly."""
        result = self.api._get_response_rest(
            "https://api.github.com/repos/test"
        )
        assert result == [{"id": 1, "name": "repo1"}]
        mock_handle_rate_limit.assert_called_once_with(
            self.mock_get.return_value
        )

    def test_unauthorized_request(self, caplog):
        """Test handling of an unauthorized (401) response."""
        self.mock_get.return_value.status_code = 401
        self.mock_get.return_value.raise_for_status.side_effect = (
            requests.HTTPError(response=self.mock_get.return_value)
        )

        with caplog.at_level(logging.WARNING):
            result = self.api._get_response_rest(
                "https://api.github.com/repos/test"
            )
            assert result == []
            assert "Unauthorized request." in caplog.text

    def test_general_http_error(self):
        """Test handling of a general HTTP error (e.g., 500)."""
        self.mock_get.return_value.status_code = 500
        self.mock_get.return_value.raise_for_status.side_effect = (
            requests.HTTPError(response=self.mock_get.return_value)
        )

        with pytest.raises(requests.HTTPError):
            self.api._get_response_rest("https://api.github.com/repos/test")
