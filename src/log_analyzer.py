import os
import requests
import openai

def fetch_logs(logs_url):
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }
    response = requests.get(logs_url, headers=headers)
    response.raise_for_status()
    return response.text

def analyze_logs(logs_url):
    logs = fetch_logs(logs_url)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Analyze the following logs and determine the cause of failure:\n\n{logs}",
        max_tokens=150
    )
    return response.choices[0].text
