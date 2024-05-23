import os
import requests
import openai

def fetch_logs(logs_url):
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(logs_url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching logs: {e}")
        return "Error fetching logs.", False
    return response.text, True

def analyze_logs(logs_url):
    logs, status = fetch_logs(logs_url)
    messages = [{"role": "user", "content": f"Analyze the following logs and determine the cause of failure:\n\n{logs}"}]
    openai.api_key = os.getenv("CHATGPT_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    print(response)
    return response.choices[0].message["content"]

