#!/usr/bin/env python3
"""
Unit tests for client.GithubOrgClient.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock, call
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
# Import fixtures for the integration test
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        # Set the mock to return the expected payload
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        
        # Access the .org property
        result = client.org

        # Assert the result is correct
        self.assertEqual(result, expected_payload)

        # Assert get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL from org payload."""
        # This is the known payload we expect 'org' property to return
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Patch 'org' as a property using PropertyMock
        with patch.object(
            GithubOrgClient, 'org', new_callable=PropertyMock
        ) as mock_org:
            
            # Set the return value of the mocked 'org' property
            mock_org.return_value = known_payload
            
            client = GithubOrgClient("google")
            
            # Access the _public_repos_url property
            result = client._public_repos_url
            
            # Assert it returns the correct URL from the payload
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the expected list of repo names."""
        # This is the payload get_json will return (a list of repo dicts)
        json_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = json_payload

        # This is the URL we expect _public_repos_url to return
        test_repos_url = "https://api.github.com/orgs/test/repos"

        # Patch the _public_repos_url property
        with patch.object(
            GithubOrgClient, '_public_repos_url', new_callable=PropertyMock
        ) as mock_public_repos_url:
            
            # Set the return value for the patched property
            mock_public_repos_url.return_value = test_repos_url

            client = GithubOrgClient("test")
            
            # Call the method under test
            repos_list = client.public_repos()

            # Assert the list of names is correct
            self.assertEqual(repos_list, ["repo1", "repo2", "repo3"])

            # Assert both mocks were called once
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


# Use parameterized_class to run integration tests with different fixtures
@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
    # You can add more fixture dictionaries here if needed
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixture for integration tests."""
        
        # Define the side_effect function for requests.get
        # This function will check the URL and return the correct fixture
        def get_side_effect(url):
            mock_response = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                # Optional: handle unexpected URLs
                mock_response.status_code = 404
            return mock_response

        # Start the patcher for 'requests.get'
        cls.get_patcher = patch('requests.get', side_effect=get_side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixture."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos method with integration setup."""
        # Create client with the org name from the fixture
        client = GithubOrgClient(self.org_payload["login"])
        
        # Call the method
        repos = client.public_repos()
        
        # Assert the result matches the expected list of repo names
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos method with a license filter."""
        client = GithubOrgClient(self.org_payload["login"])
        
        # Call with the "apache-2.0" license
        repos = client.public_repos(license="apache-2.0")
        
        # Assert the result matches the apache2_repos fixture
        self.assertEqual(repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()