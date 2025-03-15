# Engine tool registry
import sys
import os
import logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)
from engine.tool_framework import run_tool, BaseTool

# Other imports goes here
import subprocess
import re

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Tool implementation
@run_tool
class DebTool(BaseTool):
    """
    A tool to query information about Debian packages installed on the system.

    Args:
        query (str): The package name or pattern to search for.

    Returns:
        A string containing information about the specified Debian package(s) or an error message.
    """

    def deb(self, query: str):
        try:
            # Check if the query is empty
            if not query:
                return "Error: Please provide a package name or pattern to search for."
            
            # Sanitize the input to prevent command injection
            if not re.match(r'^[a-zA-Z0-9\-\+\.]+$', query):
                return "Error: Invalid package name. Package names can only contain alphanumeric characters, hyphens, plus signs, and periods."
            
            # Run dpkg command to get package information
            result = subprocess.run(['dpkg', '-l', query], 
                                   capture_output=True, 
                                   text=True)
            
            # Check if the package was found
            if "No packages found matching" in result.stdout or not result.stdout.strip():
                # Try apt-cache search as a fallback
                result = subprocess.run(['apt-cache', 'search', query], 
                                       capture_output=True, 
                                       text=True)
                if result.stdout.strip():
                    return f"Package '{query}' not installed, but found in repositories:\n{result.stdout}"
                else:
                    return f"No information found for package '{query}'."
            
            return result.stdout
        except Exception as e:
            logger.error(f"Error in DebTool: {e}", exc_info=True)
            return f"Error: {e}"