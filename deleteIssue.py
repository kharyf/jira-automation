import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
EMAIL = os.getenv('JIRA_EMAIL')
API_TOKEN = os.getenv('JIRA_API_TOKEN')
DOMAIN = "loxodonta.atlassian.net" # Change this to your domain

def delete_jira_issue():
    # Prompt user for the issue code (e.g., DG-4)
    issue_key = input("Enter the issue key to delete (e.g., DG-4): ").strip()

    if not issue_key:
        print("Error: No issue key provided.")
        return

    # Construct the Jira REST API v3 URL for the specific issue
    url = f"https://{DOMAIN}/rest/api/3/issue/{issue_key}"

    headers = {
        "Accept": "application/json"
    }

    # Confirm before deleting (Safety step)
    confirm = input(f"Are you sure you want to delete {issue_key}? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    # Perform the DELETE request
    response = requests.request(
        "DELETE",
        url,
        headers=headers,
        auth=(EMAIL, API_TOKEN)
    )

    # Handle the response
    if response.status_code == 204:
        print(f"Successfully deleted issue {issue_key}.")
    elif response.status_code == 404:
        print(f"Error: Issue {issue_key} not found.")
    elif response.status_code == 401:
        print("Error: Authentication failed. Check your API token.")
    else:
        print(f"Failed to delete issue. Status Code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    delete_jira_issue()