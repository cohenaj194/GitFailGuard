import os
import requests
import openai


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
        print(f"Error: Unable to fetch logs, status code: {response.status_code}")
        return False


def extract_info_from_url(url):
    # Split the URL by '/'
    parts = url.split("/")

    # Extract repository owner, repository name, run ID, and job ID from the URL
    repo_owner = parts[3]
    repo_name = parts[4]
    run_id = parts[7]
    job_id = parts[9]

    return repo_owner, repo_name, run_id, job_id


def cleanup_logs(logs):
    # split by newline
    logs = logs.split("\n")
    # find the index of all lines containing ##[endgroup]
    endgroup_indices = [i for i, line in enumerate(logs) if "##[endgroup]" in line]
    # find the index of the line containing ##[error]
    error_index = [i for i, line in enumerate(logs) if "##[error]" in line]

    if len(error_index) == 0:
        return "No error found in logs"

    # get all logs between the last ##[endgroup] and the first ##[error] including he line with ##[error]
    cleaned_logs = logs[endgroup_indices[-1] : error_index[0] + 1]
    return "\n".join(cleaned_logs)


def analyze_logs(logs_url):
    repo_owner, repo_name, run_id, job_id = extract_info_from_url(logs_url)
    logs = fetch_logs(repo_owner, repo_name, run_id, job_id)
    if not logs:
        return False
    logs = cleanup_logs(logs)
    prompt = "Analyze the following logs, determine the cause of failure and make a recommendation for a fix"
    messages = [
        {
            "role": "user",
            "content": f"{prompt}:\n\n{logs}",
        }
    ]
    openai.api_key = os.getenv("CHATGPT_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    print(response)
    return response.choices[0].message["content"]
