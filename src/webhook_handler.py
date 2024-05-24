import os
import requests
import json
from flask import request, jsonify
from log_analyzer import analyze_logs
from github_issue_creator import create_github_issue


def webhook():
    data = request.json
    print(json.dumps(data))
    if (
        data["action"] == "completed"
        and data["workflow_job"]["conclusion"] == "failure"
    ):
        repo_name = data["repository"]["full_name"]
        workflow_name = data["workflow_job"]["name"]
        logs_url = data["workflow_job"]["html_url"]
        analysis = analyze_logs(logs_url)
        if not analysis:
            return jsonify({"status": "error", "data": data, "issue_url": None}), 500
        else:
            issue_url = create_github_issue(
                repo_name, workflow_name, logs_url, analysis
            )
            return (
                jsonify({"status": "received", "data": data, "issue_url": issue_url}),
                200,
            )
    else:
        return jsonify({"status": "no error or not completed", "data": data, "issue_url": None}), 200