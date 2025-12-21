#!/usr/bin/env python3
"""
5 Most Common Jira Automation Rules for Loxodonta Project

This script demonstrates how to implement the 5 most common Jira automation patterns:
1. Auto-assign issues to reporter when created
2. Auto-transition to "In Progress" when issue is assigned
3. Send notification when issue status changes
4. Auto-add labels based on issue type
5. Auto-add comment when issue priority changes

Requirements:
    pip install requests python-dotenv

Usage:
    python jira_automation_rules.py
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import datetime


class JiraAutomation:
    """Wrapper class for Jira automation rules."""
    
    def __init__(self, base_url, email, api_token, project_key):
        """
        Initialize the Jira Automation client.
        
        Args:
            base_url: Jira instance URL (e.g., https://loxodonta.atlassian.net)
            email: Your Atlassian account email
            api_token: Your Jira API token
            project_key: Project key (e.g., KAN)
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.project_key = project_key
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Make an API request to Jira.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                auth=self.auth,
                json=data,
                params=params
            )
            return response
        except Exception as e:
            print(f"❌ Error making request: {e}")
            return None
    
    # ========================================================================
    # AUTOMATION RULE 1: Auto-assign issues to reporter when created
    # ========================================================================
    def auto_assign_to_reporter(self, issue_key):
        """
        Automation Rule 1: Auto-assign issue to its reporter.
        
        Trigger: When an issue is created
        Action: Assign the issue to the person who created it
        
        Args:
            issue_key: The issue key (e.g., KAN-1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("AUTOMATION RULE 1: Auto-assign to Reporter".center(70))
        print("="*70)
        
        # Get issue details to find the reporter
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to get issue {issue_key}")
            return False
        
        issue_data = response.json()
        reporter = issue_data.get('fields', {}).get('reporter', {})
        reporter_account_id = reporter.get('accountId')
        reporter_name = reporter.get('displayName', 'Unknown')
        
        if not reporter_account_id:
            print(f"❌ Could not find reporter for {issue_key}")
            return False
        
        # Assign the issue to the reporter
        update_data = {
            "fields": {
                "assignee": {
                    "accountId": reporter_account_id
                }
            }
        }
        
        response = self._make_request("PUT", f"/rest/api/3/issue/{issue_key}", data=update_data)
        
        if response and response.status_code == 204:
            print(f"✅ Successfully assigned {issue_key} to reporter: {reporter_name}")
            return True
        else:
            print(f"❌ Failed to assign {issue_key}")
            if response:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
            return False
    
    # ========================================================================
    # AUTOMATION RULE 2: Auto-transition to "In Progress" when assigned
    # ========================================================================
    def auto_transition_on_assignment(self, issue_key):
        """
        Automation Rule 2: Auto-transition issue to "In Progress" when assigned.
        
        Trigger: When an issue is assigned to someone
        Condition: Issue is not already in "In Progress" or "Done"
        Action: Transition the issue to "In Progress"
        
        Args:
            issue_key: The issue key (e.g., KAN-1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("AUTOMATION RULE 2: Auto-transition on Assignment".center(70))
        print("="*70)
        
        # Get current issue status
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to get issue {issue_key}")
            return False
        
        issue_data = response.json()
        current_status = issue_data.get('fields', {}).get('status', {}).get('name', '')
        assignee = issue_data.get('fields', {}).get('assignee', {})
        
        if not assignee:
            print(f"ℹ️  Issue {issue_key} has no assignee. Skipping transition.")
            return False
        
        # Don't transition if already in progress or done
        if current_status.lower() in ['in progress', 'done', 'closed']:
            print(f"ℹ️  Issue {issue_key} is already in '{current_status}'. No transition needed.")
            return True
        
        # Get available transitions
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}/transitions")
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to get transitions for {issue_key}")
            return False
        
        transitions = response.json().get('transitions', [])
        
        # Find "In Progress" transition (check various common names)
        in_progress_transition = None
        for transition in transitions:
            transition_name = transition.get('name', '').lower()
            if 'progress' in transition_name or transition_name == 'start':
                in_progress_transition = transition.get('id')
                break
        
        if not in_progress_transition:
            print(f"ℹ️  No 'In Progress' transition available for {issue_key}")
            print(f"   Available transitions: {[t.get('name') for t in transitions]}")
            return False
        
        # Perform the transition
        transition_data = {
            "transition": {
                "id": in_progress_transition
            }
        }
        
        response = self._make_request("POST", f"/rest/api/3/issue/{issue_key}/transitions", data=transition_data)
        
        if response and response.status_code == 204:
            print(f"✅ Successfully transitioned {issue_key} to 'In Progress'")
            return True
        else:
            print(f"❌ Failed to transition {issue_key}")
            if response:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
            return False
    
    # ========================================================================
    # AUTOMATION RULE 3: Send notification when status changes
    # ========================================================================
    def notify_on_status_change(self, issue_key, old_status, new_status):
        """
        Automation Rule 3: Add comment notification when status changes.
        
        Trigger: When an issue status changes
        Action: Add a comment notifying the assignee and watchers
        
        Args:
            issue_key: The issue key (e.g., KAN-1)
            old_status: Previous status
            new_status: New status
            
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("AUTOMATION RULE 3: Notify on Status Change".center(70))
        print("="*70)
        
        # Get issue details
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to get issue {issue_key}")
            return False
        
        issue_data = response.json()
        assignee = issue_data.get('fields', {}).get('assignee', {})
        assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
        
        # Create notification comment
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment_body = f"""
🔄 *Status Update*

Issue status changed from *{old_status}* to *{new_status}*

Assignee: {assignee_name}
Timestamp: {timestamp}

This is an automated notification from the Jira Automation system.
        """.strip()
        
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"🔄 Status Update\n\nIssue status changed from '{old_status}' to '{new_status}'\n\nAssignee: {assignee_name}\nTimestamp: {timestamp}\n\nThis is an automated notification from the Jira Automation system."
                            }
                        ]
                    }
                ]
            }
        }
        
        response = self._make_request("POST", f"/rest/api/3/issue/{issue_key}/comment", data=comment_data)
        
        if response and response.status_code == 201:
            print(f"✅ Successfully added status change notification to {issue_key}")
            return True
        else:
            print(f"❌ Failed to add comment to {issue_key}")
            if response:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
            return False
    
    # ========================================================================
    # AUTOMATION RULE 4: Auto-add labels based on issue type
    # ========================================================================
    def auto_label_by_issue_type(self, issue_key):
        """
        Automation Rule 4: Automatically add labels based on issue type.
        
        Trigger: When an issue is created or issue type changes
        Action: Add appropriate labels (e.g., "bug" label for Bug issues)
        
        Args:
            issue_key: The issue key (e.g., KAN-1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("AUTOMATION RULE 4: Auto-label by Issue Type".center(70))
        print("="*70)
        
        # Get issue details
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to get issue {issue_key}")
            return False
        
        issue_data = response.json()
        issue_type = issue_data.get('fields', {}).get('issuetype', {}).get('name', '').lower()
        existing_labels = issue_data.get('fields', {}).get('labels', [])
        
        # Map issue types to labels
        label_mapping = {
            'bug': 'bug',
            'story': 'feature',
            'task': 'task',
            'epic': 'epic',
            'sub-task': 'subtask',
            'improvement': 'enhancement'
        }
        
        new_label = label_mapping.get(issue_type)
        
        if not new_label:
            print(f"ℹ️  No label mapping defined for issue type: {issue_type}")
            return True
        
        if new_label in existing_labels:
            print(f"ℹ️  Label '{new_label}' already exists on {issue_key}")
            return True
        
        # Add the new label
        updated_labels = existing_labels + [new_label]
        update_data = {
            "fields": {
                "labels": updated_labels
            }
        }
        
        response = self._make_request("PUT", f"/rest/api/3/issue/{issue_key}", data=update_data)
        
        if response and response.status_code == 204:
            print(f"✅ Successfully added label '{new_label}' to {issue_key} (Issue Type: {issue_type})")
            return True
        else:
            print(f"❌ Failed to add label to {issue_key}")
            if response:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
            return False
    
    # ========================================================================
    # AUTOMATION RULE 5: Auto-comment on priority change
    # ========================================================================
    def auto_comment_on_priority_change(self, issue_key, old_priority, new_priority):
        """
        Automation Rule 5: Add comment when issue priority changes.
        
        Trigger: When issue priority changes
        Condition: Priority changed to High or Critical
        Action: Add a comment alerting the team
        
        Args:
            issue_key: The issue key (e.g., KAN-1)
            old_priority: Previous priority
            new_priority: New priority
            
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("AUTOMATION RULE 5: Auto-comment on Priority Change".center(70))
        print("="*70)
        
        # Only notify on high or critical priorities
        high_priorities = ['high', 'highest', 'critical', 'blocker']
        
        if new_priority.lower() not in high_priorities:
            print(f"ℹ️  Priority changed to '{new_priority}' - no notification needed")
            return True
        
        # Get issue details
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to get issue {issue_key}")
            return False
        
        issue_data = response.json()
        assignee = issue_data.get('fields', {}).get('assignee', {})
        assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
        summary = issue_data.get('fields', {}).get('summary', 'No summary')
        
        # Create priority change alert comment
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        emoji = "🔴" if new_priority.lower() in ['critical', 'blocker', 'highest'] else "🟠"
        
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{emoji} PRIORITY ALERT\n\nThis issue's priority has been changed from '{old_priority}' to '{new_priority}'.\n\nAssignee: {assignee_name}\nSummary: {summary}\nTimestamp: {timestamp}\n\n⚠️ Please review this issue as soon as possible.\n\nThis is an automated alert from the Jira Automation system."
                            }
                        ]
                    }
                ]
            }
        }
        
        response = self._make_request("POST", f"/rest/api/3/issue/{issue_key}/comment", data=comment_data)
        
        if response and response.status_code == 201:
            print(f"✅ Successfully added priority alert comment to {issue_key}")
            print(f"   Priority changed: {old_priority} → {new_priority}")
            return True
        else:
            print(f"❌ Failed to add comment to {issue_key}")
            if response:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
            return False
    
    # ========================================================================
    # Helper method to get issue details
    # ========================================================================
    def get_issue_details(self, issue_key):
        """
        Get detailed information about an issue.
        
        Args:
            issue_key: The issue key (e.g., KAN-1)
            
        Returns:
            dict: Issue details or None if failed
        """
        response = self._make_request("GET", f"/rest/api/3/issue/{issue_key}")
        
        if response and response.status_code == 200:
            return response.json()
        return None


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def print_menu():
    """Print the automation rules menu."""
    print("\n" + "="*70)
    print("JIRA AUTOMATION RULES - LOXODONTA PROJECT".center(70))
    print("="*70)
    print("\nAvailable Automation Rules:")
    print("\n1. 🤖 Auto-assign Issue to Reporter")
    print("   Automatically assigns new issues to the person who created them")
    print("\n2. ⚡ Auto-transition to 'In Progress' on Assignment")
    print("   Moves issue to 'In Progress' when someone is assigned")
    print("\n3. 📢 Notify on Status Change")
    print("   Adds notification comment when issue status changes")
    print("\n4. 🏷️  Auto-label by Issue Type")
    print("   Automatically adds appropriate labels based on issue type")
    print("\n5. ⚠️  Alert on Priority Change")
    print("   Adds urgent alert when priority is changed to High/Critical")
    print("\n0. Exit")
    print("="*70)


def main():
    """Main function to run automation rules."""
    # Load environment variables
    load_dotenv()
    
    base_url = os.getenv('JIRA_URL', 'https://loxodonta.atlassian.net')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    project_key = 'KAN'  # Default project from user's info
    
    if not email or not api_token:
        print("❌ Error: JIRA_EMAIL and JIRA_API_TOKEN must be set in .env file")
        return
    
    # Initialize automation client
    automation = JiraAutomation(base_url, email, api_token, project_key)
    
    print_header("JIRA AUTOMATION RULES DEMO")
    print(f"Connected to: {base_url}")
    print(f"Project: {project_key}")
    
    while True:
        print_menu()
        
        choice = input("\nSelect an automation rule to test (0-5): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        
        if choice not in ['1', '2', '3', '4', '5']:
            print("\n❌ Invalid choice. Please select 0-5.")
            continue
        
        # Get issue key for all rules
        issue_key = input(f"\nEnter issue key (e.g., {project_key}-1): ").strip().upper()
        
        if not issue_key:
            print("❌ Issue key is required.")
            continue
        
        # Execute the selected automation rule
        try:
            if choice == '1':
                automation.auto_assign_to_reporter(issue_key)
            
            elif choice == '2':
                automation.auto_transition_on_assignment(issue_key)
            
            elif choice == '3':
                old_status = input("Enter old status (e.g., To Do): ").strip()
                new_status = input("Enter new status (e.g., In Progress): ").strip()
                automation.notify_on_status_change(issue_key, old_status or "Unknown", new_status or "Unknown")
            
            elif choice == '4':
                automation.auto_label_by_issue_type(issue_key)
            
            elif choice == '5':
                old_priority = input("Enter old priority (e.g., Medium): ").strip()
                new_priority = input("Enter new priority (e.g., High): ").strip()
                automation.auto_comment_on_priority_change(issue_key, old_priority or "Unknown", new_priority or "Unknown")
        
        except Exception as e:
            print(f"\n❌ Error executing automation rule: {e}")
        
        input("\n\nPress Enter to continue...")


if __name__ == "__main__":
    main()
