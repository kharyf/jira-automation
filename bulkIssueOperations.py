#!/usr/bin/env python3
"""
Jira Bulk Issue Creator

Demonstrates creating multiple issues in a single request.
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

def main():
    load_dotenv()
    jira_url = os.getenv('JIRA_URL').rstrip('/')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')

    project_key = input("Enter project key for bulk creation (e.g., KAN): ").strip().upper()
    prefix = input("Enter prefix for issue summaries: ").strip()
    count = input("How many issues to create? (1-10): ").strip()
    
    try:
        count = int(count)
        if not (1 <= count <= 10): raise ValueError
    except ValueError:
        print("Invalid count. Using 2.")
        count = 2

    url = f"{jira_url}/rest/api/3/issue/bulk"
    
    issue_updates = []
    for i in range(1, count + 1):
        issue_updates.append({
            "fields": {
                "project": {"key": project_key},
                "summary": f"{prefix} - Bulk Issue #{i}",
                "issuetype": {"name": "Task"}
            }
        })

    payload = {"issueUpdates": issue_updates}

    print(f"\n⏳ Creating {count} issues in bulk...")
    response = requests.post(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=payload
    )

    if response.status_code == 201:
        result = response.json()
        created = result.get('issues', [])
        errors = result.get('errors', [])
        
        print(f"✅ Successfully created {len(created)} issue(s).")
        for iss in created:
            print(f"  - Created: {iss['key']}")
        
        if errors:
            print(f"⚠️  Encountered {len(errors)} error(s).")
    else:
        print(f"❌ Bulk operation failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
