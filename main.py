# Engine tool registry
import sys
import os
import logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)
from engine.tool_framework import run_tool, BaseTool

# Other imports goes here
import random

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Tool implementation
@run_tool
class DemoTool(BaseTool):
    """
    A demonstration tool that showcases the basic structure and functionality of a tool.
    
    This tool generates a random number and returns a greeting message with the number.
    It serves as an example for creating new tools.

    Args:
        name (str): The name to include in the greeting message

    Returns:
        A greeting message with a random number
    """

    def demo(self, name: str):
        try:
            # Generate a random number between 1 and 100
            random_number = random.randint(1, 100)
            
            # Create and return a greeting message
            result = f"Hello {name}! This is a demo tool. Your random number is: {random_number}"
            return result
        except Exception as e:
            logger.error(f"Error in DemoTool: {e}", exc_info=True)
            return f"Error: {e}"