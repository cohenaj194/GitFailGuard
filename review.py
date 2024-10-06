import os
import requests
import sys
from datetime import datetime, timedelta
import openai  # Import OpenAI library

# Replace 'owner' and 'repo' with your GitHub repository details
OWNER = "ff14-advanced-market-search"
REPO = "Aetheryte"

# GitHub API endpoints
BASE_URL = "https://api.github.com"
PULLS_URL = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls"
ISSUE_COMMENTS_URL_TEMPLATE = f"{BASE_URL}/repos/{OWNER}/{REPO}/issues/{{}}/comments"
REVIEW_COMMENTS_URL_TEMPLATE = f"{BASE_URL}/repos/{OWNER}/{REPO}/pulls/{{}}/comments"

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

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# HTTP headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_pull_requests():
    """Fetch all pull requests that had activity in the past week."""
    prs = []
    page = 1
    one_week_ago = datetime.utcnow() - timedelta(days=14)
    while True:
        params = {
            "state": "all",
            "per_page": 100,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        response = requests.get(PULLS_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        page_prs = response.json()
        if not page_prs:
            break

        for pr in page_prs:
            updated_at = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
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


def get_issue_comments(pr_number):
    """Fetch issue comments for a pull request."""
    comments_url = ISSUE_COMMENTS_URL_TEMPLATE.format(pr_number)
    response = requests.get(comments_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_review_comments(pr_number):
    """Fetch review comments for a pull request."""
    comments_url = REVIEW_COMMENTS_URL_TEMPLATE.format(pr_number)
    response = requests.get(comments_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def is_stale(pr):
    """Determine if a PR is stale (no activity for 30 days)."""
    last_updated = datetime.strptime(pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
    return datetime.utcnow() - last_updated > timedelta(days=30)


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
    for comment in comments:
        commenter = comment["user"]["login"]
        if commenter.lower() in ["coderabbitai", "coderabbit"]:
            continue
        user_comments.append(comment)

    if not user_comments:
        return None  # No conversations to summarize

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
        insights = [bp.strip("- ").strip() for bp in bullet_points if bp.strip()]
        return insights[:4]  # Limit to 4 insights
    except Exception as e:
        print(f"Error summarizing conversations: {e}")
        return ["Conversations summary not available."]


def generate_report():
    prs = get_pull_requests()
    if not prs:
        print("No pull requests with activity in the past week.")
        return

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
        elif pr_draft:
            state_icon = "🟡 Draft"
        elif pr_state == "open":
            state_icon = "🟢 Open"
        elif pr_state == "closed" and not pr_merged:
            state_icon = "🔴 Closed"
        else:
            state_icon = "⚫ Unknown"

        print(f"PR State: {state_icon}")
        print(f"* Title: **{pr_title}**, {pr_html_url}")

        # Blockers for open PRs
        if state_icon == "🟢 Open":
            print(f"* Blockers:")
            blockers = []
            if pr_mergeable is False:
                blockers.append("Needs rebase")
            if pr["requested_reviewers"]:
                reviewers = ", ".join([u["login"] for u in pr["requested_reviewers"]])
                blockers.append(f"Waiting for review from {reviewers}")
            if not blockers:
                blockers.append("Waiting for merge")
            print("  " + ", ".join(blockers))

        # Generate summary using OpenAI
        pr_summary = summarize_text(pr_body)

        # Summary line
        summary_status = (
            "Merged" if pr_merged else "Mergeable" if pr_mergeable else "Not Mergeable"
        )
        stale_text = " (Stale)" if pr_is_stale and state_icon == "🟢 Open" else ""
        print(f"* Summary: {pr_summary}, {summary_status}{stale_text}")

        # Conversations
        issue_comments = get_issue_comments(pr_number)
        review_comments = get_review_comments(pr_number)
        all_comments = issue_comments + review_comments

        # Summarize conversations if there are user comments
        insights = summarize_conversations(all_comments)
        if insights:
            print(f"* Conversations:")
            for insight in insights:
                print(f"  - {insight}")
        else:
            # Do not add a Conversations section if only bot comments exist
            pass

        print()  # Add space between PRs


if __name__ == "__main__":
    generate_report()
