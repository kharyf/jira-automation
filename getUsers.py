#!/usr/bin/env python3
"""
Jira User Searcher

Search for Jira users by name or email.
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

    query = input("Enter search query (name or email): ").strip()
    if not query: return

    url = f"{jira_url}/rest/api/3/user/search"
    params = {"query": query}
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"},
        params=params
    )

    if response.status_code == 200:
        users = response.json()
        print(f"\n✅ Found {len(users)} user(s):")
        for u in users:
            print(f"- {u['displayName']} ({u.get('emailAddress', 'Hidden Email')})")
            print(f"  Account ID: {u['accountId']}")
            print(f"  Active: {u['active']}")
            print("-" * 30)
    else:
        print(f"❌ Failed to search users (Status: {response.status_code})")

if __name__ == "__main__":
    main()
