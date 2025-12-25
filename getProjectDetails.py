#!/usr/bin/env python3
"""
Jira Project Details Fetcher

Retrieve details for a specific Jira project.
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

def main():
    load_dotenv()
    jira_url = os.getenv('JIRA_URL').rstrip('/')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    project_key = input("Enter project key (e.g., KAN): ").strip().upper()
    if not project_key: return

    url = f"{jira_url}/rest/api/3/project/{project_key}"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )

    if response.status_code == 200:
        p = response.json()
        print(f"\n✅ Project: {p['name']} ({p['key']})")
        print(f"ID: {p['id']}")
        print(f"Lead: {p.get('lead', {}).get('displayName', 'Unknown')}")
        print(f"Type: {p.get('projectTypeKey')}")
        print(f"Category: {p.get('projectCategory', {}).get('name', 'None')}")
        
        issue_types = [it['name'] for it in p.get('issueTypes', [])]
        print(f"Issue Types: {', '.join(issue_types)}")
    else:
        print(f"❌ Failed to fetch project (Status: {response.status_code})")

if __name__ == "__main__":
    main()
