#!/usr/bin/env python3
import unittest
from parameterized import parameterized
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        with self.assertRaises(KeyError) as err:
            access_nested_map(nested_map, path)
        self.assertEqual(str(err.exception), str(path[-1]))

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
        expected_result = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_result
        
        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)
        
        # Call the org property/method
        result = client.org
        
        # Assert that the result is correct
        self.assertEqual(result, expected_result)
        
        # Assert that get_json was called once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def memoize(fn):
    """Decorator to cache the result of a method."""
    attr_name = f'_memoize_{fn.__name__}'
    
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    
    return wrapper


class TestMemoize(unittest.TestCase):
    """Test cases for memoize decorator."""
    
    def test_memoize(self):
        """Test that memoize caches method results."""
        
        class TestClass:
            
            def a_method(self):
                return 42
            
            @memoize
            def a_property(self):
                return self.a_method()
        
        # Create an instance of TestClass
        test_obj = TestClass()
        
        # Patch a_method on the instance
        with patch.object(test_obj, 'a_method', return_value=42) as mock_method:
            # Call a_property twice
            result1 = test_obj.a_property()
            result2 = test_obj.a_property()
            
            # Assert the correct result is returned both times
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            
            # Assert a_method was called only once (memoization working)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()