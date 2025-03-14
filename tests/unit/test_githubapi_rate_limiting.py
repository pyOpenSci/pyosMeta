import time
from unittest.mock import Mock, patch

from pyosmeta.github_api import GitHubAPI


class TestGitHubAPI:
    def setup_method(self):
        """Set up an instance of GitHubAPI before each test."""
        self.api = GitHubAPI()

    def test_no_rate_limit(self):
        """Test when rate limit is not reached (should not sleep)."""
        mock_response = Mock(headers={"X-RateLimit-Remaining": "10"})
        with patch("time.sleep") as mock_sleep:
            self.api.handle_rate_limit(mock_response)
            mock_sleep.assert_not_called()

    def test_rate_limit_reached(self):
        """Test when rate limit is exhausted (should sleep until reset)."""
        mock_response = Mock(
            headers={
                "X-RateLimit-Remaining": "0",
                # Reset in 10 seconds
                "X-RateLimit-Reset": str(int(time.time()) + 10),
            }
        )
        with patch("time.sleep") as mock_sleep:
            self.api.handle_rate_limit(mock_response)
            # Sleep should be called once
            mock_sleep.assert_called_once()
            sleep_time = mock_sleep.call_args[0][0]
            assert 9 <= sleep_time <= 11

    def test_missing_headers(self):
        """Test when rate limit headers are missing (should do nothing)."""
        mock_response = Mock(headers={})  # No rate limit headers
        with patch("time.sleep") as mock_sleep:
            self.api.handle_rate_limit(mock_response)
            mock_sleep.assert_not_called()
