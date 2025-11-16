#!/usr/bin/env python3
"""
Unit tests for client.GithubOrgClient.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock, call
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        # Define an example payload
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org  # Access the property

        # Assert the result is correct
        self.assertEqual(result, test_payload)

        # Assert get_json was called once with the expected URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL."""
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Patch 'org' as a property using PropertyMock
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
        # Payload for get_json (list of repo dicts)
        json_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = json_payload

        # Value for _public_repos_url property
        test_repos_url = "https://api.github.com/orgs/test/repos"

        # Patch _public_repos_url as a property
        with patch.object(
            GithubOrgClient, '_public_repos_url', new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_repos_url

            client = GithubOrgClient("test")
            repos_list = client.public_repos()

            # Test result
            self.assertEqual(repos_list, ["repo1", "repo2", "repo3"])

            # Test mocks
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


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos
    },
    {
        "org_payload": org_payload,
        "repos_payload": apache2_repos,
        "expected_repos": [r["name"] for r in apache2_repos]
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixture for integration tests."""
        # Define the routes and their corresponding payloads based on fixtures
        route_payloads = {
            cls.org_payload["repos_url"]: cls.repos_payload,
            f"https://api.github.com/orgs/{cls.org_payload['login']}":
                cls.org_payload,
        }

        # Define the side_effect function for requests.get
        def get_side_effect(url):
            if url in route_payloads:
                mock_response = Mock()
                mock_response.json.return_value = route_payloads[url]
                return mock_response
            # Handle unexpected URLs
            return Mock(status_code=404)

        # Start the patcher
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


if __name__ == "__main__":
    unittest.main()