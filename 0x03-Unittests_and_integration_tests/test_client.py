#!/usr/bin/env python3
"""
Unit tests for client.GithubOrgClient.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock, call
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
# Corrected import: Import the main TEST_PAYLOAD list from fixtures
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org
        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL."""
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        # Fixed E501: Broke the long 'with' statement
        with patch.object(
            GithubOrgClient, 'org', new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = known_payload
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the expected list of repo names."""
        json_payload = [
            {"name": "repo1"}, {"name": "repo2"}, {"name": "repo3"}
        ]
        mock_get_json.return_value = json_payload

        test_repos_url = "https://api.github.com/orgs/test/repos"
        with patch.object(
            GithubOrgClient, '_public_repos_url', new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_repos_url
            client = GithubOrgClient("test")
            repos_list = client.public_repos()

            self.assertEqual(repos_list, ["repo1", "repo2", "repo3"])
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test the has_license static method."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


# Corrected decorator: This now uses the imported TEST_PAYLOAD
# This fixes the Task 8 decorator check and the Task 4/6/7 import errors
@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixture for integration tests."""
        def get_side_effect(url):
            mock_response = Mock()
            # Fixed E501: broke this long line by creating a variable
            org_url = f"https://api.github.com/orgs/{cls.org_payload['login']}"
            if url == org_url:
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.status_code = 404
            return mock_response

        cls.get_patcher = patch('requests.get', side_effect=get_side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixture."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos method with integration setup."""
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos method with a license filter."""
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
