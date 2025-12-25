#!/usr/bin/env python3
"""
Jira Comment Adder

Add a comment to an existing Jira issue.
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
    comment_text = input("Enter comment: ").strip()

    if not all([issue_key, comment_text]):
        print("❌ Error: Issue key and comment text are required.")
        return

    url = f"{jira_url}/rest/api/3/issue/{issue_key}/comment"
    
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment_text}]
                }
            ]
        }
    }

    response = requests.post(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=payload
    )

    if response.status_code == 201:
        print(f"✅ Comment added to {issue_key}")
    else:
        print(f"❌ Failed to add comment: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
