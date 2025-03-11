import unittest
import sys
import os
import random
from unittest.mock import patch

# Import the module containing the function to be tested
# Assuming the DemoTool class is in a file called demo_tool.py in the code_tool_folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

# Import the DemoTool class
# Note: This import path might need adjustment based on the actual location
from engine.tool_framework import BaseTool
from code_tool_folder.demo_tool import DemoTool

class TestDemoTool(unittest.TestCase):
    def setUp(self):
        """Set up a DemoTool instance for testing"""
        self.demo_tool = DemoTool()
    
    def test_demo_normal_case(self):
        """Test the demo method with a normal input"""
        # Use patch to control the random number for consistent testing
        with patch('random.randint', return_value=42):
            result = self.demo_tool.demo("John")
            self.assertEqual(result, "Hello John! This is a demo tool. Your random number is: 42")
    
    def test_demo_empty_name(self):
        """Test the demo method with an empty string as name"""
        with patch('random.randint', return_value=50):
            result = self.demo_tool.demo("")
            self.assertEqual(result, "Hello ! This is a demo tool. Your random number is: 50")
    
    def test_demo_special_characters(self):
        """Test the demo method with special characters in the name"""
        with patch('random.randint', return_value=75):
            result = self.demo_tool.demo("User@123!#")
            self.assertEqual(result, "Hello User@123!#! This is a demo tool. Your random number is: 75")
    
    def test_demo_long_name(self):
        """Test the demo method with a very long name"""
        long_name = "A" * 1000  # A name with 1000 'A's
        with patch('random.randint', return_value=99):
            result = self.demo_tool.demo(long_name)
            self.assertEqual(result, f"Hello {long_name}! This is a demo tool. Your random number is: 99")
    
    def test_demo_random_range(self):
        """Test that the random number is within the expected range (1-100)"""
        # Run the demo multiple times and check that all numbers are in range
        for _ in range(100):
            result = self.demo_tool.demo("Test")
            # Extract the number from the result string
            number_str = result.split(":")[-1].strip()
            number = int(number_str)
            self.assertTrue(1 <= number <= 100)
    
    @patch('random.randint', side_effect=Exception("Random error"))
    def test_demo_exception_handling(self, mock_randint):
        """Test that exceptions are properly handled"""
        result = self.demo_tool.demo("Test")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Random error", result)

if __name__ == '__main__':
    unittest.main()