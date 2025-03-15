import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path to import the module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

# Import the class to be tested
from engine.tool_framework import BaseTool
# Assuming the file is located at engine/tools/job_search/job_search_tool.py
from engine.tools.job_search.job_search_tool import JobSearchTool

class TestJobSearchTool(unittest.TestCase):
    def setUp(self):
        self.job_search_tool = JobSearchTool()
    
    def test_search_jobs_default_salary(self):
        """Test the search_jobs method with default salary range."""
        result = self.job_search_tool.search_jobs()
        
        # Check that the result is a string
        self.assertIsInstance(result, str)
        
        # Check that the result contains expected information
        self.assertIn("Found", result)
        self.assertIn("remote Rust engineering positions", result)
        self.assertIn("San Francisco", result)
        self.assertIn("Senior Rust Engineer", result)
        self.assertIn("TechCorp Inc.", result)
        self.assertIn("$145,000", result)
    
    def test_search_jobs_custom_salary(self):
        """Test the search_jobs method with a custom salary range."""
        result = self.job_search_tool.search_jobs("$130,000-150,000")
        
        # Check that the result is a string
        self.assertIsInstance(result, str)
        
        # Check that the result contains expected information
        self.assertIn("Found", result)
        
        # Should include jobs in the range
        self.assertIn("Senior Rust Engineer", result)
        self.assertIn("Rust Backend Developer", result)
        
        # Should not include jobs outside the range
        self.assertNotIn("FinTech Solutions", result)
    
    def test_search_jobs_no_results(self):
        """Test the search_jobs method with a salary range that has no matches."""
        # Patch the mock API to return no matching jobs
        with patch.object(JobSearchTool, '_mock_job_search_api') as mock_api:
            mock_api.return_value = {"jobs": []}
            result = self.job_search_tool.search_jobs()
            
            # Check that the result indicates no jobs were found
            self.assertEqual(result, "No jobs found matching your criteria.")
    
    def test_search_jobs_invalid_salary_format(self):
        """Test the search_jobs method with an invalid salary format."""
        # Test with invalid salary format
        result = self.job_search_tool.search_jobs("invalid_salary")
        
        # Should return an error message
        self.assertIn("Error:", result)
    
    def test_search_jobs_api_error(self):
        """Test the search_jobs method when the API call raises an exception."""
        # Patch the mock API to raise an exception
        with patch.object(JobSearchTool, '_mock_job_search_api') as mock_api:
            mock_api.side_effect = Exception("API connection error")
            result = self.job_search_tool.search_jobs()
            
            # Check that the result contains the error message
            self.assertIn("Error: API connection error", result)
    
    def test_mock_job_search_api(self):
        """Test the _mock_job_search_api method."""
        result = self.job_search_tool._mock_job_search_api("Rust", "San Francisco", "remote", 120000, 150000)
        
        # Check that the result is a dictionary with a 'jobs' key
        self.assertIsInstance(result, dict)
        self.assertIn("jobs", result)
        
        # Check that the 'jobs' value is a list
        self.assertIsInstance(result["jobs"], list)
        
        # Check that the list contains job dictionaries with expected keys
        for job in result["jobs"]:
            self.assertIsInstance(job, dict)
            self.assertIn("title", job)
            self.assertIn("company", job)
            self.assertIn("location", job)
            self.assertIn("salary", job)
            self.assertIn("description", job)
            self.assertIn("remote", job)
            self.assertIn("skills", job)

if __name__ == '__main__':
    unittest.main()