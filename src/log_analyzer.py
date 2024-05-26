import os
import requests
import openai

from github_issue_creator import post_comment_to_pull_request


def fetch_logs(repo_owner, repo_name, run_id, job_id):
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/jobs/{job_id}/logs"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(
            f"Error: Unable to fetch logs from {url}, status code: {response.status_code}"
        )
        return False


def extract_info_from_url(url):
    try:
        # Split the URL by '/'
        parts = url.split("/")
        # Extract repository owner, repository name, run ID, and job ID from the URL
        repo_owner = parts[3]
        repo_name = parts[4]
        run_id = parts[7]
        job_id = parts[9]
        return repo_owner, repo_name, run_id, job_id
    except Exception as e:
        print(f"Error: Unable to fetch logs from {url}: {e}")
        return None, None, None, None


def cleanup_logs(logs, logs_url):
    # split by newline
    logs = logs.split("\n")
    # find the index of all lines containing ##[group]
    group_indices = [i for i, line in enumerate(logs) if "##[group]" in line]
    # find the index of the line containing ##[error]
    error_index = [i for i, line in enumerate(logs) if "##[error]" in line]
    if len(error_index) == 0:
        print(f"No error found in logs for: {logs_url}")
        return False
    # get all logs between the last ##[group] and the first ##[error] including the line with ##[error]
    cleaned_logs = logs[group_indices[-1] : error_index[0] + 1]
    return "\n".join(cleaned_logs)


def analyze_logs(logs_url, head_branch):
    repo_owner, repo_name, run_id, job_id = extract_info_from_url(logs_url)

    # return error if logs url not properly split
    if None in [repo_owner, repo_name, run_id, job_id]:
        return False

    # get raw logs
    logs = fetch_logs(repo_owner, repo_name, run_id, job_id)

    # return error if we cant get logs
    if not logs:
        return False

    # cleanup logs and get only the error portion
    logs = cleanup_logs(logs, logs_url)

    # return error if no errors found in logs
    if not logs:
        return False

    # send comment to pull request if pr_number is found
    enable_coderabbit = os.getenv("ENABLE_CODERABBIT")
    # Check if the branch has an active pull request and ping the CodeRabbit bot if so
    comment_url = None
    if enable_coderabbit:
        comment_url = ping_coderabbit(
            repo_owner, repo_name, head_branch, logs, logs_url
        )

    prompt = (
        "You are a helpful AI assistant named GitFailGuard."
        + " Analyze the following logs, determine the cause of failure and make a recommendation for a fix"
    )
    messages = [
        {
            "role": "user",
            "content": f"{prompt}:\n\n{logs}",
        }
    ]
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    print(response)
    issue_body = response.choices[0].message["content"]
    if comment_url:
        issue_body += f"\n\n[CodeRabbit has been notified to review the logs of this run.]({comment_url})"

    return issue_body


def ping_coderabbit(repo_owner, repo_name, head_branch, logs, logs_url):
    pr_number = get_pull_request_number(repo_owner, repo_name, head_branch)
    if pr_number:
        pr_comment = (
            f"@coderabbitai review the logs from [the failed workflow job]({logs_url}) "
            + f" related to this PR:\n\n```\n{logs}\n```"
        )
        comment_url = post_comment_to_pull_request(
            repo_owner, repo_name, pr_number, pr_comment
        )
        print(f"Comment to PR posted successfully: {comment_url}")
        return comment_url


def get_pull_request_number(repo_owner, repo_name, head_branch):
    if not head_branch:
        return None
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    prs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    response = requests.get(
        prs_url,
        headers=headers,
        params={"state": "open", "head": f"{repo_owner}:{head_branch}"},
    )
    response.raise_for_status()
    prs = response.json()

    if prs:
        return prs[0]["number"]
    return None
