#!/usr/bin/env python3
"""
Jira Issue Worklog Fetcher

Retrieve worklogs for a specific Jira issue.
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

    issue_key = input("Enter issue key (e.g., KAN-1): ").strip().upper()
    if not issue_key: return

    url = f"{jira_url}/rest/api/3/issue/{issue_key}/worklog"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )

    if response.status_code == 200:
        worklogs = response.json().get('worklogs', [])
        print(f"\n✅ Found {len(worklogs)} worklog(s) for {issue_key}:")
        for wl in worklogs:
            author = wl.get('author', {}).get('displayName', 'Unknown')
            time = wl.get('timeSpent')
            created = wl.get('created')
            print(f"- {time} logged by {author} on {created}")
            if wl.get('comment'):
                print(f"  Comment: {wl['comment']}")
    else:
        print(f"❌ Failed to fetch worklogs (Status: {response.status_code})")

if __name__ == "__main__":
    main()
