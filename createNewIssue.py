#!/usr/bin/env python3
"""
Interactive Jira Issue Creator

This script provides an interactive way to create new Jira issues.
Simply run the script and follow the prompts to create a new issue.

Requirements:
    pip install requests python-dotenv

Usage:
    python createNewIssue.py
    or
    py -3.13 createNewIssue.py
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def print_section(text):
    """Print a formatted section header."""
    print("\n" + "-"*70)
    print(text)
    print("-"*70)


def get_input(prompt, default=None, required=True):
    """Get user input with optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while required:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input
            print("⚠️  This field is required. Please enter a value.")
        return input(f"{prompt} (optional): ").strip()


def get_choice(prompt, options):
    """Get user choice from a list of options."""
    print(f"\n{prompt}")
    for idx, option in enumerate(options, 1):
        print(f"  {idx}. {option}")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                return options[choice_idx]
            else:
                print(f"⚠️  Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("⚠️  Please enter a valid number")


def get_yes_no(prompt, default=True):
    """Get yes/no input from user."""
    default_str = "Y/n" if default else "y/N"
    while True:
        choice = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not choice:
            return default
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("⚠️  Please enter 'y' or 'n'")


def get_projects(base_url, email, api_token):
    """Fetch available projects from Jira."""
    url = f"{base_url}/rest/api/3/project"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️  Warning: Could not fetch projects (Status: {response.status_code})")
        return []


def get_issue_types(base_url, email, api_token, project_key):
    """Fetch available issue types for a project."""
    url = f"{base_url}/rest/api/3/project/{project_key}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={"Accept": "application/json"}
    )
    
    if response.status_code == 200:
        project_data = response.json()
        return project_data.get('issueTypes', [])
    else:
        return []


def create_issue(base_url, email, api_token, issue_data):
    """Create a new issue in Jira."""
    url = f"{base_url}/rest/api/3/issue"
    
    response = requests.post(
        url,
        auth=HTTPBasicAuth(email, api_token),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json=issue_data
    )
    
    return response


def build_description_adf(text):
    """Build Atlassian Document Format (ADF) for description."""
    if not text:
        return None
    
    # Split by newlines to create paragraphs
    paragraphs = text.split('\n')
    content = []
    
    for para in paragraphs:
        if para.strip():
            content.append({
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": para
                    }
                ]
            })
    
    if not content:
        return None
    
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def main():
    """Main function for interactive issue creation."""
    
    # Load environment variables
    load_dotenv()
    
    print_header("🎫 JIRA ISSUE CREATOR 🎫")
    
    # Get credentials from environment
    jira_url = os.getenv('JIRA_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, email, api_token]):
        print("❌ Error: Missing required environment variables in .env file!")
        print("\nPlease ensure your .env file contains:")
        print("  JIRA_URL=https://your-domain.atlassian.net")
        print("  JIRA_EMAIL=your-email@example.com")
        print("  JIRA_API_TOKEN=your-api-token")
        return
    
    jira_url = jira_url.rstrip('/')
    print(f"📡 Connected to: {jira_url}\n")
    
    # Fetch available projects
    print("🔍 Fetching available spaces...")
    projects = get_projects(jira_url, email, api_token)
    
    if not projects:
        print("❌ No spaces found. Please check your credentials.")
        return
    
    print(f"✓ Found {len(projects)} space(s)")
    
    # Step 1: Select Project
    print_section("STEP 1: Select Space")
    
    print("\nAvailable spaces:")
    for idx, project in enumerate(projects, 1):
        print(f"  {idx}. {project['key']} - {project['name']}")
    
    while True:
        project_input = get_input("\nEnter space key (e.g., KAN)", projects[0]['key'] if projects else None)
        project_key = project_input.upper()
        
        # Find the project
        selected_project = next((p for p in projects if p['key'] == project_key), None)
        if selected_project:
            print(f"✓ Selected: {selected_project['name']} ({selected_project['key']})")
            break
        else:
            print(f"⚠️  Space '{project_key}' not found. Please try again.")
    
    # Step 2: Select Issue Type
    print_section("STEP 2: Select Issue Type")
    
    print("\n🔍 Fetching issue types...")
    issue_types = get_issue_types(jira_url, email, api_token, project_key)
    
    if not issue_types:
        print("⚠️  Could not fetch issue types. Using default 'Task'")
        issue_type_name = "Task"
        issue_type_id = None
    else:
        # Filter out subtasks
        issue_types = [it for it in issue_types if not it.get('subtask', False)]
        
        print("\nAvailable issue types:")
        for idx, it in enumerate(issue_types, 1):
            print(f"  {idx}. {it['name']}")
        
        issue_type_choice = get_choice("Select issue type:", [it['name'] for it in issue_types])
        selected_issue_type = next(it for it in issue_types if it['name'] == issue_type_choice)
        issue_type_name = selected_issue_type['name']
        issue_type_id = selected_issue_type['id']
        print(f"✓ Selected: {issue_type_name}")
    
    # Step 3: Issue Details
    print_section("STEP 3: Issue Details")
    
    summary = get_input("\nIssue summary (title)", required=True)
    
    print("\nIssue description (press Enter twice to finish, or just Enter to skip):")
    description_lines = []
    empty_line_count = 0
    
    while empty_line_count < 1:
        line = input()
        if line.strip():
            description_lines.append(line)
            empty_line_count = 0
        else:
            empty_line_count += 1
    
    description_text = '\n'.join(description_lines).strip()
    description_adf = build_description_adf(description_text) if description_text else None
    
    # Step 4: Priority (optional)
    print_section("STEP 4: Additional Fields (Optional)")
    
    set_priority = get_yes_no("\nSet priority?", False)
    priority_name = None
    
    if set_priority:
        priority_name = get_choice(
            "Select priority:",
            ["Highest", "High", "Medium", "Low", "Lowest"]
        )
        print(f"✓ Priority: {priority_name}")
    
    # Step 5: Labels (optional)
    add_labels = get_yes_no("\nAdd labels?", False)
    labels = []
    
    if add_labels:
        labels_input = get_input("Enter labels (comma-separated)", required=False)
        if labels_input:
            labels = [label.strip() for label in labels_input.split(',')]
            print(f"✓ Labels: {', '.join(labels)}")
    
    # Step 6: Review and Create
    print_section("STEP 5: Review Issue")
    
    print(f"\n📋 Issue Summary:")
    print(f"  Space: {project_key}")
    print(f"  Type: {issue_type_name}")
    print(f"  Summary: {summary}")
    if description_text:
        preview = description_text[:100] + "..." if len(description_text) > 100 else description_text
        print(f"  Description: {preview}")
    if priority_name:
        print(f"  Priority: {priority_name}")
    if labels:
        print(f"  Labels: {', '.join(labels)}")
    
    # Build the issue payload
    issue_payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "issuetype": {
                "name": issue_type_name
            }
        }
    }
    
    if issue_type_id:
        issue_payload["fields"]["issuetype"]["id"] = issue_type_id
    
    if description_adf:
        issue_payload["fields"]["description"] = description_adf
    
    if priority_name:
        issue_payload["fields"]["priority"] = {"name": priority_name}
    
    if labels:
        issue_payload["fields"]["labels"] = labels
    
    # Show full JSON if requested
    if get_yes_no("\nShow full JSON payload?", False):
        print("\n📄 Issue JSON:")
        print(json.dumps(issue_payload, indent=2))
    
    # Confirm creation
    if not get_yes_no("\n🚀 Create this issue now?", True):
        print("\n❌ Issue creation cancelled.")
        return
    
    # Create the issue
    print("\n⏳ Creating issue...")
    
    response = create_issue(jira_url, email, api_token, issue_payload)
    
    if response.status_code == 201:
        result = response.json()
        issue_key = result.get('key')
        issue_id = result.get('id')
        issue_url = f"{jira_url}/browse/{issue_key}"
        
        print("\n✅ SUCCESS! Issue created!")
        print(f"\n📋 Issue Details:")
        print(f"  Key: {issue_key}")
        print(f"  ID: {issue_id}")
        print(f"  URL: {issue_url}")
        print(f"\n🔗 View in Jira: {issue_url}")
    else:
        print(f"\n❌ Failed to create issue (Status: {response.status_code})")
        print(f"\nError response:")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
        except:
            print(response.text[:500])
    
    print("\n" + "="*70)
    print("Thank you for using the Jira Issue Creator!".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
