#!/usr/bin/env python3
"""Unit tests for GithubOrgClient."""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""
    
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        # Set up the mock return value
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload
        
        # Create an instance of GithubOrgClient
        github_org_client = GithubOrgClient(org_name)
        
        # Call the org property
        result = github_org_client.org
        
        # Assert that the result is correct
        self.assertEqual(result, test_payload)
        
        # Assert that get_json was called once with the expected URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class."""
    
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
        # Set up the mock return value
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload
        
        # Create an instance of GithubOrgClient
        github_org_client = GithubOrgClient(org_name)
        
        # Call the org property
        result = github_org_client.org
        
        # Assert that the result is correct
        self.assertEqual(result, test_payload)
        
        # Assert that get_json was called once with the expected URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
    
    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL."""
        # Known payload with repos_url
        known_payload = {
            "login": "google",
            "id": 1342004,
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        
        # Use patch as a context manager to mock the org property
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=lambda: property(lambda self: known_payload)
        ):
            # Create an instance of GithubOrgClient
            github_org_client = GithubOrgClient("google")
            
            # Access the _public_repos_url property
            result = github_org_client._public_repos_url
            
            # Assert that the result matches the repos_url from the payload
            self.assertEqual(result, known_payload["repos_url"])

        


if __name__ == "__main__":
    unittest.main()