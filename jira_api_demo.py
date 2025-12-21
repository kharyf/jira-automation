#!/usr/bin/env python3
"""
Demonstration of the 7 Most Basic Jira API Calls

This script demonstrates:
1. Getting server information
2. Getting a specific issue
3. Searching for issues using JQL
4. Getting space information
5. Getting issue transitions
6. Creating a new issue
7. Deleting an issue

Requirements:
    pip install requests

Usage:
    Set the following environment variables:
    - JIRA_URL: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
    - JIRA_EMAIL: Your Atlassian account email
    - JIRA_API_TOKEN: Your Jira API token (create at https://id.atlassian.com/manage-profile/security/api-tokens)
    
    Then run:
    python jira_api_demo.py
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth


class JiraAPIDemo:
    """Simple wrapper for demonstrating basic Jira API calls."""
    
    def __init__(self, base_url, email, api_token):
        """
        Initialize the Jira API client.
        
        Args:
            base_url: Jira instance URL (e.g., https://your-domain.atlassian.net)
            email: Your Atlassian account email
            api_token: Your Jira API token
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, **kwargs):
        """
        Make an authenticated request to the Jira API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object or None if error
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def get_server_info(self):
        """
        API Call #1: Get Jira Server Information
        
        This is the simplest API call - it returns basic information about
        your Jira instance without requiring any parameters.
        
        Endpoint: GET /rest/api/3/serverInfo
        """
        print("\n" + "="*70)
        print("API CALL #1: Get Server Information")
        print("="*70)
        
        response = self._make_request("GET", "/rest/api/3/serverInfo")
        if response:
            data = response.json()
            print(f"Server Version: {data.get('version')}")
            print(f"Build Number: {data.get('buildNumber')}")
            print(f"Base URL: {data.get('baseUrl')}")
            print(f"Deployment Type: {data.get('deploymentType')}")
            return data
        return None
    
    def get_issue(self, issue_key):
        """
        API Call #2: Get a Specific Issue
        
        Retrieve detailed information about a specific Jira issue using its key.
        
        Args:
            issue_key: Issue key (e.g., 'KAN-1')
            
        Endpoint: GET /rest/api/3/issue/{issueIdOrKey}
        """
        print("\n" + "="*70)
        print(f"API CALL #2: Get Issue '{issue_key}'")
        print("="*70)
        
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        if response:
            data = response.json()
            fields = data.get('fields', {})
            print(f"Key: {data.get('key')}")
            print(f"Summary: {fields.get('summary')}")
            print(f"Status: {fields.get('status', {}).get('name')}")
            print(f"Issue Type: {fields.get('issuetype', {}).get('name')}")
            print(f"Priority: {fields.get('priority', {}).get('name')}")
            print(f"Assignee: {fields.get('assignee', {}).get('displayName') if fields.get('assignee') else 'Unassigned'}")
            print(f"Reporter: {fields.get('reporter', {}).get('displayName')}")
            print(f"Created: {fields.get('created')}")
            return data
        return None
    
    def search_issues(self, jql, max_results=5):
        """
        API Call #3: Search Issues Using JQL
        
        Search for issues using JQL (Jira Query Language).
        This is one of the most powerful Jira API calls.
        
        Args:
            jql: JQL query string (e.g., 'space = KAN AND status = "To Do"')
            max_results: Maximum number of results to return
            
        Endpoint: GET /rest/api/3/search
        """
        print("\n" + "="*70)
        print(f"API CALL #3: Search Issues with JQL")
        print(f"Query: {jql}")
        print("="*70)
        
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,priority,issuetype"
        }
        
        response = self._make_request("GET", "/rest/api/3/search", params=params)
        if response:
            data = response.json()
            total = data.get('total', 0)
            issues = data.get('issues', [])
            
            print(f"Total Issues Found: {total}")
            print(f"Showing {len(issues)} issue(s):\n")
            
            for issue in issues:
                fields = issue.get('fields', {})
                print(f"  {issue.get('key')}: {fields.get('summary')}")
                print(f"    Status: {fields.get('status', {}).get('name')}")
                print(f"    Type: {fields.get('issuetype', {}).get('name')}")
                print()
            
            return data
        return None
    
    def get_space(self, space_key):
        """
        API Call #4: Get Space Information
        
        Retrieve detailed information about a specific space.
        
        Args:
            space_key: Space key (e.g., 'KAN')
            
        Endpoint: GET /rest/api/3/project/{projectIdOrKey}
        """
        print("\n" + "="*70)
        print(f"API CALL #4: Get Space '{space_key}'")
        print("="*70)
        
        response = self._make_request("GET", f"/rest/api/3/project/{space_key}")
        if response:
            data = response.json()
            print(f"Key: {data.get('key')}")
            print(f"Name: {data.get('name')}")
            print(f"Space Type: {data.get('projectTypeKey')}")
            print(f"Lead: {data.get('lead', {}).get('displayName')}")
            print(f"Description: {data.get('description', 'No description')}")
            
            # Show issue types
            issue_types = data.get('issueTypes', [])
            if issue_types:
                print(f"\nAvailable Issue Types:")
                for it in issue_types:
                    print(f"  - {it.get('name')}")
            
            return data
        return None
    
    def get_issue_transitions(self, issue_key):
        """
        API Call #5: Get Available Transitions for an Issue
        
        Get the list of available workflow transitions for an issue.
        This is useful to know what actions can be performed on an issue.
        
        Args:
            issue_key: Issue key (e.g., 'KAN-1')
            
        Endpoint: GET /rest/api/3/issue/{issueIdOrKey}/transitions
        """
        print("\n" + "="*70)
        print(f"API CALL #5: Get Transitions for Issue '{issue_key}'")
        print("="*70)
        
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}/transitions")
        if response:
            data = response.json()
            transitions = data.get('transitions', [])
            
            if transitions:
                print(f"Available transitions for {issue_key}:\n")
                for transition in transitions:
                    print(f"  ID: {transition.get('id')}")
                    print(f"  Name: {transition.get('name')}")
                    print(f"  To Status: {transition.get('to', {}).get('name')}")
                    print()
            else:
                print(f"No transitions available for {issue_key}")
            
            return data
        return None
    
    def create_issue(self, space_key, summary, issue_type="Task", description="", priority="Medium"):
        """
        API Call #6: Create a New Issue
        
        Create a new issue in a Jira space.
        
        Args:
            space_key: Space key (e.g., 'KAN')
            summary: Issue summary/title
            issue_type: Type of issue (e.g., 'Task', 'Bug', 'Story')
            description: Issue description
            priority: Priority level (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest')
            
        Endpoint: POST /rest/api/3/issue
        """
        print("\n" + "="*70)
        print(f"API CALL #6: Create Issue in Space '{space_key}'")
        print("="*70)
        
        payload = {
            "fields": {
                "project": {
                    "key": space_key
                },
                "summary": summary,
                "issuetype": {
                    "name": issue_type
                },
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        # Add priority if provided
        if priority:
            payload["fields"]["priority"] = {"name": priority}
        
        response = self._make_request("POST", "/rest/api/3/issue", json=payload)
        if response:
            data = response.json()
            issue_key = data.get('key')
            issue_id = data.get('id')
            
            print(f"✓ Issue created successfully!")
            print(f"  Key: {issue_key}")
            print(f"  ID: {issue_id}")
            print(f"  Summary: {summary}")
            print(f"  Type: {issue_type}")
            
            return data
        return None
    
    def delete_issue(self, issue_key):
        """
        API Call #7: Delete an Issue
        
        Delete an issue permanently from Jira.
        WARNING: This action cannot be undone!
        
        Args:
            issue_key: Issue key to delete (e.g., 'KAN-1')
            
        Endpoint: DELETE /rest/api/3/issue/{issueIdOrKey}
        """
        print("\n" + "="*70)
        print(f"API CALL #7: Delete Issue '{issue_key}'")
        print("="*70)
        print("⚠️  WARNING: This will permanently delete the issue!")
        
        response = self._make_request("DELETE", f"/rest/api/3/issue/{issue_key}")
        if response:
            # DELETE returns 204 No Content on success
            print(f"✓ Issue '{issue_key}' deleted successfully!")
            return True
        else:
            print(f"✗ Failed to delete issue '{issue_key}'")
            return False


def main():
    """Main function to demonstrate all 7 basic Jira API calls."""
    
    # Get credentials from environment variables
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    
    # Validate credentials
    if not all([jira_url, jira_email, jira_api_token]):
        print("Error: Missing required environment variables!")
        print("\nPlease set the following environment variables:")
        print("  JIRA_URL - Your Jira instance URL (e.g., https://your-domain.atlassian.net)")
        print("  JIRA_EMAIL - Your Atlassian account email")
        print("  JIRA_API_TOKEN - Your Jira API token")
        print("\nCreate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens")
        return
    
    # Initialize the Jira client
    print("="*70)
    print("JIRA API DEMONSTRATION - 7 Basic API Calls")
    print("="*70)
    print(f"Connecting to: {jira_url}")
    
    jira = JiraAPIDemo(jira_url, jira_email, jira_api_token)
    
    # Example values - modify these for your Jira instance
    SPACE_KEY = "KAN"  # Your space key
    ISSUE_KEY = "KAN-3"  # An existing issue in your space
    
    # Execute the 7 basic API calls
    try:
        # 1. Get server information
        jira.get_server_info()
        
        # 2. Get a specific issue
        jira.get_issue(ISSUE_KEY)
        
        # 3. Search for issues using JQL
        jql_query = f'project = {SPACE_KEY} ORDER BY created DESC'
        jira.search_issues(jql_query, max_results=5)
        
        # 4. Get space information
        jira.get_space(SPACE_KEY)
        
        # 5. Get available transitions for an issue
        jira.get_issue_transitions(ISSUE_KEY)
        
        # 6. Create a new issue (optional - uncomment to test)
        # new_issue = jira.create_issue(
        #     space_key=SPACE_KEY,
        #     summary="Test Issue Created via API",
        #     issue_type="Task",
        #     description="This is a test issue created using the Jira REST API.",
        #     priority="Medium"
        # )
        # if new_issue:
        #     new_issue_key = new_issue.get('key')
        #     print(f"\nCreated issue: {new_issue_key}")
        
        # 7. Delete an issue (optional - uncomment to test)
        # WARNING: This permanently deletes the issue!
        # if new_issue:
        #     jira.delete_issue(new_issue_key)
        
        print("\n" + "="*70)
        print("DEMONSTRATION COMPLETE!")
        print("="*70)
        print("\nAll 7 basic Jira API calls executed successfully.")
        print("\nNext steps:")
        print("  - Modify the SPACE_KEY and ISSUE_KEY variables for your data")
        print("  - Uncomment the create_issue and delete_issue calls to test them")
        print("  - Explore the Jira API documentation: https://developer.atlassian.com/cloud/jira/platform/rest/v3/")
        print("  - Try modifying the JQL queries to search for different issues")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
