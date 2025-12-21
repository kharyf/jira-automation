#!/usr/bin/env python3
"""
Get Jira Project Details

Simple script that performs one GET request to fetch project details
and saves them to a local JSON file.

Requirements:
    pip install requests python-dotenv

Usage:
    python get_automation_rules.py
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
CLOUD_ID=os.getenv('CLOUD_ID')
PROJECT_KEY = 'LOX'
PROTOCOL = 'https'
HOST = 'api.atlassian.com'

# API endpoint
url = f"{PROTOCOL}://{HOST}/automation/public/jira/{CLOUD_ID}/rest/v1/rule/summary"

# Make GET request
response = requests.get(
    url,
    headers={"Accept": "application/json"},
    auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
)

# Remove Identifiable key
data=response.json()
keys_to_remove = ["authorAccountId", "actorAccountId", "ruleScopeARIs"]
for item in data['data']:
    for key in keys_to_remove:
        item.pop(key,None)

# Save response to JSON file
output_file = f"{PROJECT_KEY}_automation_rules.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"✅ Saved to {output_file}")
print(f"Status: {response.status_code}")
