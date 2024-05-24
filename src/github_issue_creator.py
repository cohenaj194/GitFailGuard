import os
import requests


def create_github_issue(repo_name, workflow_name, logs_url, analysis):
    issue_title = f"Failed GitHub Action: {workflow_name}"
    issue_body = (
        f"The GitHub Action `{workflow_name}` failed.\n\n"
        f"Logs: [View Logs]({logs_url})\n\n"
        f"Analysis:\n{analysis}"
    )
    github_api_url = f"https://api.github.com/repos/{repo_name}/issues"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"title": issue_title, "body": issue_body}
    response = requests.post(github_api_url, headers=headers, json=data)
    if response.status_code == 201:
        print("Issue created successfully.")
    else:
        print(f"Failed to create issue: {response.content}")
