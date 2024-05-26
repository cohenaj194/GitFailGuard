import os
import requests
import time
import openai


def create_github_issue(repo_name, workflow_name, logs_url, analysis):
    issue_title = f"GitFailGuard: {workflow_name} {int(time.time())}"
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
        issue_url = response.json().get("html_url")
        print(f"Issue created successfully: {issue_url}")
        return issue_url
    else:
        print(f"Failed to create issue: {response.content}")


def respond_to_issue_comment(comment_body, issue_body, issue_title):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        f"You are a helpful AI assistant named GitFailGuard. A user has commented on the issue titled '{issue_title}' "
        f"with the following description:\n\n{issue_body}\n\n"
        f"The user asked the following question:\n\n'{comment_body}'\n\n"
        "Please provide a helpful and detailed response to their question."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )
    return response.choices[0].message["content"]


def post_comment_to_pull_request(repo_owner, repo_name, pr_number, comment):
    github_token = os.getenv("GITHUB_TOKEN")
    github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"body": comment}
    response = requests.post(github_api_url, headers=headers, json=data)
    if response.status_code == 201:
        print("Comment posted successfully.")
        return response.json().get("html_url")
    else:
        print(f"Failed to post comment: {response.content}")
        return False
