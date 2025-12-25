#!/usr/bin/env python3
"""
Jira Issue Transitioner

Move an issue through its workflow.
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

    issue_key = input("Enter issue key to transition (e.g., KAN-1): ").strip().upper()
    if not issue_key: return

    # 1. Fetch available transitions
    trans_url = f"{jira_url}/rest/api/3/issue/{issue_key}/transitions"
    response = requests.get(trans_url, auth=HTTPBasicAuth(email, api_token))
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch transitions (Status: {response.status_code})")
        return

    transitions = response.json().get('transitions', [])
    if not transitions:
        print("No transitions available for this issue.")
        return

    print(f"\nAvailable transitions for {issue_key}:")
    for idx, t in enumerate(transitions, 1):
        print(f"  {idx}. {t['name']} (ID: {t['id']})")

    choice = input(f"\nSelect transition (1-{len(transitions)}): ").strip()
    try:
        selected = transitions[int(choice)-1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    # 2. Perform transition
    payload = {"transition": {"id": selected['id']}}
    resp = requests.post(
        trans_url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Content-Type": "application/json"},
        json=payload
    )

    if resp.status_code == 204:
        print(f"✅ Issue {issue_key} transitioned to: {selected['name']}")
    else:
        print(f"❌ Transition failed: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    main()
