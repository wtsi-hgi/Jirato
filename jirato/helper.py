import json
import os

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

JIRA_TOKEN = os.environ["JIRA_TOKEN"]

# Hard-coded project mapping - these IDs won't change
PROJECT_MAPPING = {
    "HI": "14101",  # HGI Informatics
    "HB": "14800",  # HGI Bioinformatics
    "HSF": "14300",  # HGI Software Farmers
    "HSH": "14301",  # HGI Software HailQC
    "HSI": "14200",  # HGI Software iBackup
    "HSS": "14202",  # HGI Software Softpack
    "HSW": "14201",  # HGI Software wrstat
}


def add_jira(
    summary,
    description,
    done,
    labels,
    name,
    project_key,
    reporter,
    parent=None,
    is_softpack_admin=False,
    is_user_story=False,
):
    """
    Create a JIRA ticket

    Args:
        summary: Ticket summary
        description: Ticket description
        done: Whether to mark as done
        labels: List of labels
        name: Assignee name
        project_key: Project key (HI, HB, etc.)
        reporter: Reporter username
        parent: Parent issue key (optional)
        is_softpack_admin: Whether this is a softpack admin ticket
        is_user_story: Whether this is a user story ticket
    """
    url = "https://jira.sanger.ac.uk/rest/api/2/issue"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": JIRA_TOKEN,
    }

    # Get project ID from hard-coded mapping
    project_id = PROJECT_MAPPING.get(project_key, "14101")  # Default to HI if not found

    # Set customfield_10110 based on softpack admin checkbox
    customfield_value = None if is_softpack_admin else "HI-229"

    # Set issue type based on user story checkbox
    issue_type_id = (
        "10001" if is_user_story else ("10003" if parent else "10002")
    )  # 10001 = Story, 10003 = Sub-task, 10002 = Task

    payload = json.dumps(
        {
            "fields": {
                "assignee": {"name": name},
                "customfield_10110": customfield_value,
                "description": description,
                "issuetype": {"id": issue_type_id},
                "labels": labels,
                "priority": {"id": "10000"},
                "project": {"id": project_id},
                "reporter": {"name": reporter},
                "summary": summary,
                "parent": {"key": parent} if parent else None,
            },
            "update": {},
        }
    )

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
    )

    if done:
        payload = json.dumps(
            {
                "transition": {"id": "41"},
            }
        )
        url_issue = f"{url}/{json.loads(response.text)['key']}/transitions"

        requests.request(
            "POST",
            url_issue,
            data=payload,
            headers=headers,
        )
    logger.info(response.text)
    print(
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )
    )
    return json.loads(response.text)["key"]


def add_comments(contents, issue_key):
    url = f"https://jira.sanger.ac.uk/rest/api/2/issue/{issue_key}/comment"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": JIRA_TOKEN,
    }
    payload = json.dumps(
        {
            "body": contents,
        }
    )

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
    )

    print(
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )
    )


def add_attachment(fp, fn, issue_key):
    url = f"https://jira.sanger.ac.uk/rest/api/2/issue/{issue_key}/attachments"

    headers = {
        "Accept": "application/json",
        "X-Atlassian-Token": "no-check",
        "Authorization": JIRA_TOKEN,
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        files={"file": (fn, fp.read_bytes(), "application-type")},
    )
    print(response.text)
    print(
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )
    )


def move_issue_to_to_do(issue):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": JIRA_TOKEN,
    }
    payload = json.dumps(
        {
            "transition": {"id": "11"},
        }
    )
    url_issue = f"https://jira.sanger.ac.uk/rest/api/2/issue/{issue}/transitions"

    response = requests.request(
        "POST",
        url_issue,
        data=payload,
        headers=headers,
    )
    print(response.text)


def get_jira_from_jql(jql):
    url = "https://jira.sanger.ac.uk/rest/api/2/search"
    headers = {"Authorization": JIRA_TOKEN}
    start_at = 0
    max_results = 50
    total = None
    all_issues = []

    while total is None or start_at < total:
        params = {"jql": jql, "startAt": start_at, "maxResults": max_results}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = json.loads(response.text)
            issues = data["issues"]
            all_issues.extend(issues)

            total = data["total"]
            start_at += len(issues)
        else:
            return f"Error: {response.status_code}, {response.text}"

    return all_issues
