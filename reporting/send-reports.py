import os
import requests
import sys
from datetime import datetime, timedelta, timezone
import openai  # Import OpenAI library

# Replace 'ORGANIZATION' with your GitHub organization name
ORGANIZATION = "ff14-advanced-market-search"

# GitHub API endpoints
BASE_URL = "https://api.github.com"
REPOS_URL = f"{BASE_URL}/orgs/{ORGANIZATION}/repos"

# Get GitHub token from environment variable
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set.")
    sys.exit(1)

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)

# Get Discord webhook URL from environment variable
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Get Slack webhook URL from environment variable
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

# **Get MS Teams webhook URL from environment variable**
MS_TEAMS_WEBHOOK = os.environ.get("MS_TEAMS_WEBHOOK")

# Check if at least one webhook URL is set
if not DISCORD_WEBHOOK_URL and not SLACK_WEBHOOK and not MS_TEAMS_WEBHOOK:
    print(
        "Error: None of the DISCORD_WEBHOOK_URL, SLACK_WEBHOOK, or MS_TEAMS_WEBHOOK environment variables are set."
    )
    sys.exit(1)


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# HTTP headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_repositories():
    """Fetch all repositories in the organization."""
    repos = []
    page = 1
    while True:
        params = {"per_page": 100, "page": page}
        response = requests.get(REPOS_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        page_repos = response.json()
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1

    # Remove the 'pr-reviewer_test' repository from the list
    repos = [repo for repo in repos if repo["name"] != "pr-reviewer_test"]

    return repos


def get_pull_requests(owner, repo):
    """Fetch all pull requests for a repository that had activity in the past week."""
    prs = []
    page = 1
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=1)
    pulls_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    while True:
        params = {
            "state": "all",
            "per_page": 100,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        response = requests.get(pulls_url, headers=HEADERS, params=params)
        response.raise_for_status()
        page_prs = response.json()
        if not page_prs:
            break

        for pr in page_prs:
            updated_at = datetime.strptime(
                pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            if updated_at >= one_week_ago:
                prs.append(pr)
            else:
                # Since the PRs are sorted by updated_at descending, we can break early
                break

        # Check if we've reached PRs older than one week
        if updated_at < one_week_ago:
            break

        page += 1

    return prs


def get_issue_comments(owner, repo, pr_number):
    """Fetch issue comments for a pull request."""
    comments_url = (
        f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    )
    response = requests.get(comments_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_review_comments(owner, repo, pr_number):
    """Fetch review comments for a pull request."""
    comments_url = (
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    )
    response = requests.get(comments_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def is_stale(pr):
    """Determine if a PR is stale (no activity for 30 days)."""
    last_updated = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    return datetime.now(timezone.utc) - last_updated > timedelta(days=30)


def summarize_text(text, max_tokens=150):
    """Use OpenAI API to summarize text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the following text in under 50 words.",
                },
                {"role": "user", "content": text},
            ],
            max_tokens=max_tokens,
            temperature=0.5,
        )
        summary = response["choices"][0]["message"]["content"].strip()
        return summary
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Summary not available."


def summarize_conversations(comments):
    """Summarize conversations from comments."""
    # Filter out bot comments and comments without user interaction
    user_comments = []
    participants = set()
    for comment in comments:
        commenter = comment["user"]["login"]
        if "[bot]" in commenter.lower() or commenter.lower() in [
            "coderabbitai",
            "coderabbit",
        ]:
            continue
        participants.add(commenter)
        user_comments.append(comment)

    if not user_comments:
        return None, None  # No conversations to summarize

    # Prepare the conversation text
    conversation_text = ""
    for comment in user_comments:
        commenter = comment["user"]["login"]
        body = comment["body"]
        conversation_text += f"{commenter}: {body}\n"

    # Use OpenAI to summarize the conversations into bullet points
    try:
        prompt = (
            "Summarize the following conversation into up to 4 bullet points, "
            "highlighting requests, recommendations, suggestions, concerns, etc. "
            "Include the names of the commenters.\n\n"
            f"{conversation_text}"
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes conversations.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.5,
        )
        summary = response["choices"][0]["message"]["content"].strip()
        bullet_points = summary.split("\n")
        # Clean up bullet points
        insights = [bp.strip("-•* ").strip() for bp in bullet_points if bp.strip()]
        return insights[:4], participants  # Limit to 4 insights
    except Exception as e:
        print(f"Error summarizing conversations: {e}")
        return ["Conversations summary not available."], participants


def send_to_slack(repo_name, report_sections):
    """Send the report to Slack via webhook."""
    if not SLACK_WEBHOOK:
        return  # Do nothing if Slack webhook is not set

    MAX_BLOCKS_PER_MESSAGE = 50
    blocks = []

    for section in report_sections:
        # Header block with PR title and state icon
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{section.get('url')}|{section.get('title')}>*",
                },
            }
        )
        # Summary
        for field in section.get("fields", []):
            if field["name"] == "Summary":
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Summary:*\n{field['value']}",
                        },
                    }
                )
        # Blockers
        for field in section.get("fields", []):
            if field["name"] == "Blockers":
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Blockers:*\n{field['value']}",
                        },
                    }
                )
        # Conversations
        for field in section.get("fields", []):
            if field["name"].startswith("Conversations"):
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{field['name']}:*\n{field['value']}",
                        },
                    }
                )
        # Divider
        blocks.append({"type": "divider"})

        # If blocks reach the limit, send the message and reset the list
        if len(blocks) >= MAX_BLOCKS_PER_MESSAGE:
            data = {"username": "GitHub PR Reporter", "blocks": blocks}
            try:
                response = requests.post(SLACK_WEBHOOK, json=data)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                print(
                    f"HTTP error occurred when sending to Slack: {http_err} - {response.text}"
                )
            except Exception as err:
                print(f"An error occurred when sending to Slack: {err}")
            else:
                print("Successfully sent message to Slack")
            blocks = []

    # Send any remaining blocks
    if blocks:
        data = {"username": "GitHub PR Reporter", "blocks": blocks}
        try:
            response = requests.post(SLACK_WEBHOOK, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(
                f"HTTP error occurred when sending to Slack: {http_err} - {response.text}"
            )
        except Exception as err:
            print(f"An error occurred when sending to Slack: {err}")
        else:
            print("Successfully sent message to Slack")


def send_to_discord(repo_name, report_sections):
    """Send the report to Discord via webhook."""
    if not DISCORD_WEBHOOK_URL:
        return  # Do nothing if Discord webhook is not set

    MAX_EMBEDS_PER_MESSAGE = 10
    embeds_list = [
        report_sections[i : i + MAX_EMBEDS_PER_MESSAGE]
        for i in range(0, len(report_sections), MAX_EMBEDS_PER_MESSAGE)
    ]

    for idx, embeds_chunk in enumerate(embeds_list):
        embeds = []
        for section in embeds_chunk:
            embed = {
                "title": section.get("title"),
                "url": section.get("url"),
                "color": section.get("color"),
                "fields": section.get("fields"),
                "footer": {"text": f"Repository: {repo_name}"},
            }
            embeds.append(embed)

        data = {"username": "GitHub PR Reporter", "embeds": embeds}

        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(
                f"HTTP error occurred on message {idx+1}: {http_err} - {response.text}"
            )
        except Exception as err:
            print(f"An error occurred on message {idx+1}: {err}")
        else:
            print(f"Successfully sent message {idx+1} to Discord")


def send_to_teams(repo_name, report_sections):
    """Send the report to Microsoft Teams via webhook."""
    if not MS_TEAMS_WEBHOOK:
        return  # Do nothing if Teams webhook is not set

    MAX_MESSAGE_SIZE = 28000  # 28KB limit for Teams messages
    sections = []
    message_size = 0

    for section in report_sections:
        # Create a section for the MessageCard
        activityTitle = f"[{section.get('title')}]({section.get('url')})"
        fields = section.get('fields', [])
        facts = []
        text = ""

        for field in fields:
            name = field.get('name')
            value = field.get('value')
            if name == 'Summary':
                # Include summary in 'text' of the section
                text = f"**Summary:** {value}"
            elif name == 'Blockers':
                facts.append({'name': 'Blockers', 'value': value})
            elif name.startswith('Conversations'):
                facts.append({'name': name, 'value': value})
            else:
                facts.append({'name': name, 'value': value})

        section_dict = {
            'activityTitle': activityTitle,
            'facts': facts,
            'text': text,
        }

        # Estimate the size of the section
        section_size = len(str(section_dict).encode('utf-8'))
        message_size += section_size

        if message_size >= MAX_MESSAGE_SIZE:
            # Send the message with current sections
            message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": f"GitHub PR Report for {repo_name}",
                "sections": sections,
            }
            try:
                response = requests.post(MS_TEAMS_WEBHOOK, json=message)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred when sending to Teams: {http_err} - {response.text}")
            except Exception as err:
                print(f"An error occurred when sending to Teams: {err}")
            else:
                print("Successfully sent message to Microsoft Teams")
            # Reset sections and message_size
            sections = [section_dict]
            message_size = section_size
        else:
            sections.append(section_dict)

    # Send any remaining sections
    if sections:
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": f"GitHub PR Report for {repo_name}",
            "sections": sections,
        }
        try:
            response = requests.post(MS_TEAMS_WEBHOOK, json=message)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred when sending to Teams: {http_err} - {response.text}")
        except Exception as err:
            print(f"An error occurred when sending to Teams: {err}")
        else:
            print("Successfully sent message to Microsoft Teams")


def generate_report():
    repos = get_repositories()
    if not repos:
        print("No repositories found in the organization.")
        return

    for repo in repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]
        prs = get_pull_requests(owner, repo_name)
        if not prs:
            continue  # Skip repositories with no recent PRs

        report_sections = []

        print(f"\nRepository: {repo_name}")

        for pr in prs:
            pr_number = pr["number"]
            pr_title = pr["title"]
            pr_body = pr["body"] or "No description provided."
            pr_state = pr["state"]
            pr_draft = pr["draft"]
            pr_merged = pr.get("merged_at") is not None
            pr_mergeable = pr.get("mergeable")
            pr_user = pr["user"]["login"]
            pr_html_url = pr["html_url"]
            pr_is_stale = is_stale(pr)

            # Determine PR State
            if pr_merged:
                state_icon = "🟣 Merged"
                color = 0x6F42C1  # Purple
            elif pr_draft:
                state_icon = "🟡 Draft"
                color = 0xF9C513  # Yellow
            elif pr_state == "open":
                state_icon = "🟢 Open"
                color = 0x28A745  # Green
            elif pr_state == "closed" and not pr_merged:
                state_icon = "🔴 Closed"
                color = 0xCB2431  # Red
            else:
                state_icon = "⚫ Unknown"
                color = 0x000000  # Black

            print(f"PR State: {state_icon}")
            print(f"* Title: **{pr_title}**, {pr_html_url}")

            fields = []

            # Blockers for open PRs
            if state_icon == "🟢 Open":
                print(f"* Blockers:")
                blockers = []
                if pr_mergeable is False:
                    blockers.append("Needs rebase")
                if pr["requested_reviewers"]:
                    reviewers = ", ".join(
                        [u["login"] for u in pr["requested_reviewers"]]
                    )
                    blockers.append(f"Waiting for review from {reviewers}")
                if not blockers:
                    blockers.append("Waiting for merge")
                blockers_text = ", ".join(blockers)
                print("  " + blockers_text)
                fields.append(
                    {"name": "Blockers", "value": blockers_text, "inline": False}
                )

            # Generate summary using OpenAI
            pr_summary = summarize_text(pr_body)

            # Summary line
            summary_status = (
                "Merged"
                if pr_merged
                else "Mergeable" if pr_mergeable else "Not Mergeable"
            )
            stale_text = " (Stale)" if pr_is_stale and state_icon == "🟢 Open" else ""
            summary_line = f"{pr_summary}, {summary_status}{stale_text}"
            print(f"* Summary: {summary_line}")
            fields.append({"name": "Summary", "value": summary_line, "inline": False})

            # Conversations
            issue_comments = get_issue_comments(owner, repo_name, pr_number)
            review_comments = get_review_comments(owner, repo_name, pr_number)
            all_comments = issue_comments + review_comments

            # Summarize conversations if there are user comments
            insights, participants = summarize_conversations(all_comments)
            if insights:
                participants_list = ", ".join(sorted(participants))
                print(f"* Conversations (Participants: {participants_list}):")
                insights_text = ""
                for insight in insights:
                    print(f"  - {insight}")
                    insights_text += f"- {insight}\n"
                fields.append(
                    {
                        "name": f"Conversations (Participants: {participants_list})",
                        "value": insights_text.strip(),
                        "inline": False,
                    }
                )

            # Prepare report section for this PR
            report_sections.append(
                {
                    "title": f"{state_icon} {pr_title}",
                    "url": pr_html_url,
                    "color": color,
                    "fields": fields,
                }
            )

            print()  # Add space between PRs

            # Send report to Discord and/or Slack for this repository
            send_to_discord(repo_name, report_sections)
            send_to_slack(repo_name, report_sections)
            send_to_teams(repo_name, report_sections)


if __name__ == "__main__":
    generate_report()
