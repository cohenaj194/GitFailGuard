import os
import requests
import json
from flask import request, jsonify
from log_analyzer import analyze_logs
from github_issue_creator import create_github_issue, respond_to_issue_comment


def webhook():
    data = request.json
    print(json.dumps(data))

    if is_failed_workflow(data):
        return handle_failed_workflow(data)
    elif is_issue_comment(data):
        return handle_issue_comment_event(data)
    else:
        return jsonify({"status": "no action taken", "data": data}), 200


def is_failed_workflow(data):
    return (
        data.get("action") == "completed"
        and data.get("workflow_job", {}).get("conclusion") == "failure"
    )


def handle_failed_workflow(data):
    repo_name = data["repository"]["full_name"]
    workflow_name = data["workflow_job"]["name"]
    logs_url = data["workflow_job"]["html_url"]

    analysis = analyze_logs(logs_url)
    if not analysis:
        return jsonify({"status": "error", "data": data, "issue_url": None}), 500

    issue_url = create_github_issue(repo_name, workflow_name, logs_url, analysis)
    return jsonify({"status": "received", "data": data, "issue_url": issue_url}), 200


def is_issue_comment(data):
    return data.get("action") == "created" and "comment" in data


def handle_issue_comment_event(data):
    if "@GitFailGuard" not in data["comment"]["body"]:
        return (
            jsonify({"status": "GitFailGuard not mentioned in comment", "data": data}),
            200,
        )

    comment_url = process_issue_comment(data)
    if not comment_url:
        return jsonify({"status": "error", "data": data, "comment_url": None}), 500

    return (
        jsonify({"status": "received", "data": data, "comment_url": comment_url}),
        200,
    )


def process_issue_comment(data):
    repo_owner = data["repository"]["owner"]["login"]
    repo_name = data["repository"]["name"]
    issue_number = data["issue"]["number"]
    comment_body = data["comment"]["body"]
    issue_body = data["issue"]["body"]
    issue_title = data["issue"]["title"]

    response = respond_to_issue_comment(issue_title, issue_body, comment_body)
    return post_comment_to_github(repo_owner, repo_name, issue_number, response)


def post_comment_to_github(repo_owner, repo_name, issue_number, comment):
    github_token = os.getenv("GITHUB_TOKEN")
    github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
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
