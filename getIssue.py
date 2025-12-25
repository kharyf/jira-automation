#!/usr/bin/env python3
"""
Jira Issue Details Fetcher

Retrieve and display details for a specific Jira issue.
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
    print_header("📄 JIRA ISSUE DETAILS")
    
    issue_key = input("Enter issue key (e.g., KAN-1): ").strip().upper()
    if not issue_key:
        print("❌ Error: Issue key is required.")
        return

    url = f"{jira_url}/rest/api/3/issue/{issue_key}"

    print(f"\n⏳ Fetching details for {issue_key}...")
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )

    if response.status_code == 200:
        issue = response.json()
        fields = issue['fields']
        
        print(f"\n✅ {issue['key']}: {fields['summary']}")
        print(f"Status: {fields['status']['name']}")
        print(f"Project: {fields['project']['name']} ({fields['project']['key']})")
        print(f"Issue Type: {fields['issuetype']['name']}")
        
        assignee = fields.get('assignee')
        print(f"Assignee: {assignee['displayName'] if assignee else 'Unassigned'}")
        
        creator = fields.get('creator')
        print(f"Creator: {creator['displayName'] if creator else 'Unknown'}")
        
        print("\nDescription:")
        # Description is in ADF format, we'll just show the raw text for simplicity or a message
        desc = fields.get('description')
        if desc:
            print("  [ADF Content Available]")
        else:
            print("  (No description)")
            
        print(f"\nURL: {jira_url}/browse/{issue_key}")
    else:
        print(f"❌ Failed to fetch issue (Status: {response.status_code})")
        if response.status_code == 404:
            print(f"Result: Issue {issue_key} not found.")

if __name__ == "__main__":
    main()
