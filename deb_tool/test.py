import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path to import the module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

# Import the module to be tested
from engine.tools.deb_tool import DebTool

class TestDebTool(unittest.TestCase):
    def setUp(self):
        self.deb_tool = DebTool()
    
    def test_deb_empty_query(self):
        """Test that an empty query returns an error message"""
        result = self.deb_tool.deb("")
        self.assertEqual(result, "Error: Please provide a package name or pattern to search for.")
    
    def test_deb_invalid_query(self):
        """Test that an invalid query with special characters returns an error message"""
        result = self.deb_tool.deb("invalid;rm -rf /")
        self.assertEqual(result, "Error: Invalid package name. Package names can only contain alphanumeric characters, hyphens, plus signs, and periods.")
    
    @patch('subprocess.run')
    def test_deb_package_found(self, mock_run):
        """Test that a valid package query returns package information"""
        # Mock the subprocess.run to return a successful result
        mock_process = MagicMock()
        mock_process.stdout = "ii  python3    3.9.5    amd64    Python interpreter"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.deb_tool.deb("python3")
        self.assertEqual(result, "ii  python3    3.9.5    amd64    Python interpreter")
        mock_run.assert_called_once_with(['dpkg', '-l', 'python3'], capture_output=True, text=True)
    
    @patch('subprocess.run')
    def test_deb_package_not_installed_but_found(self, mock_run):
        """Test that a package not installed but found in repositories returns appropriate message"""
        # First call to dpkg returns no packages found
        mock_process_dpkg = MagicMock()
        mock_process_dpkg.stdout = "No packages found matching python3-dev"
        mock_process_dpkg.stderr = ""
        
        # Second call to apt-cache returns package info
        mock_process_apt = MagicMock()
        mock_process_apt.stdout = "python3-dev - Header files and a static library for Python"
        mock_process_apt.stderr = ""
        
        mock_run.side_effect = [mock_process_dpkg, mock_process_apt]
        
        result = self.deb_tool.deb("python3-dev")
        self.assertEqual(result, "Package 'python3-dev' not installed, but found in repositories:\npython3-dev - Header files and a static library for Python")
        
        # Check that both commands were called
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(['dpkg', '-l', 'python3-dev'], capture_output=True, text=True)
        mock_run.assert_any_call(['apt-cache', 'search', 'python3-dev'], capture_output=True, text=True)
    
    @patch('subprocess.run')
    def test_deb_package_not_found(self, mock_run):
        """Test that a package not found anywhere returns appropriate message"""
        # First call to dpkg returns no packages found
        mock_process_dpkg = MagicMock()
        mock_process_dpkg.stdout = "No packages found matching nonexistentpackage"
        mock_process_dpkg.stderr = ""
        
        # Second call to apt-cache returns empty
        mock_process_apt = MagicMock()
        mock_process_apt.stdout = ""
        mock_process_apt.stderr = ""
        
        mock_run.side_effect = [mock_process_dpkg, mock_process_apt]
        
        result = self.deb_tool.deb("nonexistentpackage")
        self.assertEqual(result, "No information found for package 'nonexistentpackage'.")
        
        # Check that both commands were called
        self.assertEqual(mock_run.call_count, 2)
    
    @patch('subprocess.run')
    def test_deb_exception_handling(self, mock_run):
        """Test that exceptions are properly caught and reported"""
        # Mock subprocess.run to raise an exception
        mock_run.side_effect = Exception("Command failed")
        
        result = self.deb_tool.deb("python3")
        self.assertEqual(result, "Error: Command failed")

if __name__ == '__main__':
    unittest.main()