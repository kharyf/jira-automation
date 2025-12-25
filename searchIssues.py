#!/usr/bin/env python3
"""
Jira Issue Searcher

Search for issues using JQL (Jira Query Language).
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
    print_header("🔍 JIRA ISSUE SEARCH")
    
    jql = input("Enter JQL query (e.g., project = 'KAN' AND status = 'To Do'): ").strip()
    if not jql:
        print("⚠️  Empty JQL. Searching for all issues...")
        jql = "order by created DESC"

    url = f"{jira_url}/rest/api/3/search"
    
    payload = {
        "jql": jql,
        "maxResults": 10,
        "fields": ["summary", "status", "issuetype", "assignee"]
    }

    print("\n⏳ Searching...")
    response = requests.post(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        issues = data.get('issues', [])
        total = data.get('total', 0)
        
        print(f"✓ Found {total} issue(s). Showing top {len(issues)}:\n")
        
        for issue in issues:
            key = issue['key']
            summary = issue['fields']['summary']
            status = issue['fields']['status']['name']
            itype = issue['fields']['issuetype']['name']
            assignee = issue['fields'].get('assignee')
            assignee_name = assignee['displayName'] if assignee else "Unassigned"
            
            print(f"[{key}] {summary}")
            print(f"      Type: {itype} | Status: {status} | Assignee: {assignee_name}")
            print("-" * 50)
    else:
        print(f"❌ Search failed (Status: {response.status_code})")
        print(response.text)

if __name__ == "__main__":
    main()
