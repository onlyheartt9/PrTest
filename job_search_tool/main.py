# Engine tool registry
import sys
import os
import logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)
from engine.tool_framework import run_tool, BaseTool

# Other imports goes here
import requests
import json
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Tool implementation
@run_tool
class JobSearchTool(BaseTool):
    """
    Searches for remote Rust engineering positions in San Francisco with a specified salary range.

    Args:
        salary_range (str, optional): The salary range to filter jobs by (e.g., "$120,000-150,000").
                                     Defaults to "$120,000-150,000".

    Returns:
        A list of 3 job positions matching the criteria, including job title, company, location, 
        salary, and a brief description.
    """

    def search_jobs(self, salary_range: str = "$120,000-150,000"):
        try:
            # Parse salary range
            salary_range = salary_range.replace("$", "").replace(",", "")
            min_salary, max_salary = map(int, salary_range.split("-"))
            
            # Mock API call to job search service
            # In a real implementation, this would call an actual job search API
            mock_response = self._mock_job_search_api("Rust", "San Francisco", "remote", min_salary, max_salary)
            
            # Filter and format the results
            filtered_jobs = []
            for job in mock_response["jobs"]:
                if len(filtered_jobs) >= 3:
                    break
                    
                # Check if job matches all criteria
                if (job["remote"] and 
                    "Rust" in job["skills"] and 
                    "San Francisco" in job["location"] and
                    min_salary <= job["salary"] <= max_salary):
                    
                    filtered_jobs.append({
                        "title": job["title"],
                        "company": job["company"],
                        "location": job["location"],
                        "salary": f"${job['salary']:,}",
                        "description": job["description"][:100] + "...",
                        "remote": "Yes"
                    })
            
            # Format the output
            if not filtered_jobs:
                return "No jobs found matching your criteria."
            
            result = f"Found {len(filtered_jobs)} remote Rust engineering positions in San Francisco:\n\n"
            for i, job in enumerate(filtered_jobs, 1):
                result += f"{i}. {job['title']} at {job['company']}\n"
                result += f"   Location: {job['location']} (Remote: {job['remote']})\n"
                result += f"   Salary: {job['salary']}\n"
                result += f"   Description: {job['description']}\n\n"
                
            return result
            
        except Exception as e:
            logger.error(f"Error in JobSearchTool: {e}", exc_info=True)
            return f"Error: {e}"
    
    def _mock_job_search_api(self, skill: str, location: str, remote: str, min_salary: int, max_salary: int) -> Dict[str, Any]:
        """Mock function to simulate a job search API response"""
        return {
            "jobs": [
                {
                    "title": "Senior Rust Engineer",
                    "company": "TechCorp Inc.",
                    "location": "San Francisco, CA",
                    "salary": 145000,
                    "description": "We're looking for a senior Rust engineer to join our distributed systems team. Experience with WebAssembly and cloud infrastructure required.",
                    "remote": True,
                    "skills": ["Rust", "WebAssembly", "Distributed Systems"]
                },
                {
                    "title": "Rust Backend Developer",
                    "company": "Blockchain Innovations",
                    "location": "San Francisco, CA",
                    "salary": 135000,
                    "description": "Join our team building the next generation of blockchain infrastructure using Rust and WebAssembly.",
                    "remote": True,
                    "skills": ["Rust", "Blockchain", "Backend"]
                },
                {
                    "title": "Rust Systems Engineer",
                    "company": "Security Solutions",
                    "location": "San Francisco, CA",
                    "salary": 140000,
                    "description": "Help us build secure, high-performance systems using Rust. Experience with low-level programming and security concepts required.",
                    "remote": True,
                    "skills": ["Rust", "Systems Programming", "Security"]
                },
                {
                    "title": "Rust Developer",
                    "company": "StartupXYZ",
                    "location": "San Francisco, CA",
                    "salary": 125000,
                    "description": "Looking for a Rust developer to help build our core infrastructure. Experience with async Rust and networking required.",
                    "remote": True,
                    "skills": ["Rust", "Async", "Networking"]
                },
                {
                    "title": "Senior Rust Engineer",
                    "company": "FinTech Solutions",
                    "location": "San Francisco, CA",
                    "salary": 155000,  # Outside the range
                    "description": "Join our team building high-frequency trading systems in Rust.",
                    "remote": True,
                    "skills": ["Rust", "Finance", "Trading"]
                }
            ]
        }