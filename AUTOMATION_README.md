# Jira Automation Rules - Loxodonta Project (KAN)

This document explains the 5 most common Jira automation rules implemented for your project.

## 📋 Overview

The `jira_automation_rules.py` script implements the following automation patterns:

### 1. 🤖 Auto-assign Issue to Reporter
**Trigger:** When an issue is created  
**Action:** Automatically assigns the issue to the person who created it  
**Use Case:** Ensures accountability by default - creators are initially responsible for their issues

### 2. ⚡ Auto-transition to 'In Progress' on Assignment
**Trigger:** When an issue is assigned to someone  
**Condition:** Issue is not already in "In Progress" or "Done"  
**Action:** Automatically moves the issue to "In Progress" status  
**Use Case:** Keeps workflow moving - assignment implies work has started

### 3. 📢 Notify on Status Change
**Trigger:** When an issue status changes  
**Action:** Adds a notification comment with timestamp and assignee info  
**Use Case:** Creates an audit trail and keeps team members informed of progress

### 4. 🏷️ Auto-label by Issue Type
**Trigger:** When an issue is created or issue type changes  
**Action:** Automatically adds appropriate labels based on issue type  
**Label Mapping:**
- Bug → `bug`
- Story → `feature`
- Task → `task`
- Epic → `epic`
- Sub-task → `subtask`
- Improvement → `enhancement`

**Use Case:** Makes issues easier to filter and report on

### 5. ⚠️ Alert on Priority Change
**Trigger:** When issue priority changes to High or Critical  
**Action:** Adds an urgent alert comment to notify the team  
**Use Case:** Ensures high-priority issues get immediate attention

## 🚀 Quick Start

### Prerequisites
```bash
pip install requests python-dotenv
```

### Environment Setup
Make sure your `.env` file contains:
```
JIRA_URL=https://loxodonta.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### Run the Script
```bash
python jira_automation_rules.py
```

## 💡 Usage Examples

### Interactive Menu
The script provides an interactive menu where you can test each automation rule:

```
1. Select an automation rule (1-5)
2. Enter the issue key (e.g., KAN-1)
3. Provide any additional information if needed
4. The automation executes and shows results
```

### Example Session
```
Select an automation rule to test (0-5): 1
Enter issue key (e.g., KAN-1): KAN-123

✅ Successfully assigned KAN-123 to reporter: John Doe
```

## 🔧 Integration as Real Automation

While this script provides manual testing of automation logic, in a production environment, these rules would typically be:

1. **Configured in Jira Automation UI** (Project Settings → Automation)
2. **Triggered automatically** by webhooks
3. **Run by Jira's automation engine** without manual intervention

This script is useful for:
- ✅ Testing automation logic before deploying
- ✅ Batch processing existing issues
- ✅ Understanding how automations work
- ✅ Custom automation that Jira's UI doesn't support

## 📊 Common Use Cases by Rule

| Automation Rule | Best For | Frequency of Use |
|----------------|----------|------------------|
| Auto-assign to Reporter | Small teams, personal projects | Very Common |
| Auto-transition on Assignment | Active projects with clear workflow | Very Common |
| Notify on Status Change | Projects needing audit trails | Common |
| Auto-label by Issue Type | Large projects with many issues | Very Common |
| Alert on Priority Change | Critical/production projects | Common |

## 🛡️ Safety Notes

⚠️ **Important:** This script modifies Jira issues. Always:
- Test on non-critical issues first
- Verify your API token has appropriate permissions
- Review changes before applying to production issues
- Keep backups of important data

## 🎯 Extending the Script

You can easily add more automation rules by following the pattern:

```python
def your_automation_rule(self, issue_key, ...):
    """
    Description of your rule.
    
    Trigger: When X happens
    Action: Do Y
    """
    # 1. Get issue data
    # 2. Check conditions
    # 3. Perform action
    # 4. Return success/failure
```

## 📚 Additional Resources

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Jira Automation Documentation](https://support.atlassian.com/jira-cloud-administration/docs/automation-basics/)
- [Jira Query Language (JQL)](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

## 🤝 Support

For issues or questions:
1. Check the error messages in the console
2. Verify your API token and permissions
3. Ensure issue keys are valid
4. Review Jira audit logs for details

---

Created for the Loxodonta project (KAN) | Last updated: 2025-12-21
