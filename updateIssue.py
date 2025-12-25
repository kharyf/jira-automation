#!/usr/bin/env python3
"""
Jira Issue Updater

Update fields of an existing Jira issue.
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

def print_header(text):
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")

def main():
    load_dotenv()
    
    jira_url = os.getenv('JIRA_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, email, api_token]):
        print("❌ Error: Missing required environment variables!")
        return

    jira_url = jira_url.rstrip('/')
    print_header("✏️ JIRA ISSUE UPDATER")
    
    issue_key = input("Enter issue key to update (e.g., KAN-1): ").strip().upper()
    if not issue_key:
        return

    print("\nWhat would you like to update?")
    print("1. Summary")
    print("2. Description")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    payload = {"fields": {}}
    
    if choice in ['1', '3']:
        summary = input("Enter new summary: ").strip()
        if summary:
            payload["fields"]["summary"] = summary
            
    if choice in ['2', '3']:
        description = input("Enter new description: ").strip()
        if description:
            # Simple ADF conversion for text
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            }

    if not payload["fields"]:
        print("⚠️  No changes specified.")
        return

    url = f"{jira_url}/rest/api/3/issue/{issue_key}"

    print(f"\n⏳ Updating {issue_key}...")
    response = requests.put(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.status_code == 204:
        print(f"✅ Successfully updated {issue_key}!")
    else:
        print(f"❌ Update failed (Status: {response.status_code})")
        print(response.text)

if __name__ == "__main__":
    main()
