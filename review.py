import os
import requests
import sys
from datetime import datetime, timedelta

# Replace 'owner' and 'repo' with your GitHub repository details
OWNER = 'ff14-advanced-market-search'
REPO = 'Aetheryte'

# GitHub API endpoints
BASE_URL = 'https://api.github.com'
PULLS_URL = f'{BASE_URL}/repos/{OWNER}/{REPO}/pulls'
ISSUE_COMMENTS_URL_TEMPLATE = f'{BASE_URL}/repos/{OWNER}/{REPO}/issues/{{}}/comments'
REVIEW_COMMENTS_URL_TEMPLATE = f'{BASE_URL}/repos/{OWNER}/{REPO}/pulls/{{}}/comments'

# Get GitHub token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set.")
    sys.exit(1)

# HTTP headers for authentication
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_pull_requests():
    """Fetch all pull requests."""
    params = {'state': 'all', 'per_page': 100}
    response = requests.get(PULLS_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

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
    last_updated = datetime.strptime(pr['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
    return datetime.utcnow() - last_updated > timedelta(days=2)

def summarize_conversations(comments):
    """Summarize conversations from comments."""
    insights = []
    for comment in comments:
        commenter = comment['user']['login']
        body = comment['body']
        # Skip bot comments unless there's interaction
        if commenter.lower() == 'coderabbitai' and not any(c['user']['login'] != 'coderabbitai' for c in comments):
            continue
        # Ignore auto-generated comments by coderabbitai
        if 'auto-generated comment' in body.lower():
            continue
        # Create insight summary
        insight = f"Reviewer {commenter} says: {body[:100].replace('\n', ' ')}"
        # Check if comment is addressed (only possible in review comments)
        addressed = False
        if 'in_reply_to_id' in comment:
            # Only review comments have 'in_reply_to_id'
            addressed = any(
                c.get('id') == comment['in_reply_to_id']
                for c in comments if c.get('id') and c.get('id') != comment.get('id')
            )
        if addressed:
            insight += ' (Addressed)'
        insights.append(insight)
    if not insights:
        return ['No conversation']
    return insights[:4]  # Limit to 2 to 4 insights

def generate_report():
    prs = get_pull_requests()
    for pr in prs:
        pr_number = pr['number']
        pr_title = pr['title']
        pr_state = pr['state']
        pr_draft = pr['draft']
        pr_merged = pr.get('merged_at') is not None
        pr_mergeable = pr.get('mergeable')
        pr_user = pr['user']['login']
        pr_html_url = pr['html_url']
        pr_is_stale = is_stale(pr)

        # Determine PR State
        if pr_merged:
            state_icon = '🟣 Merged'
        elif pr_draft:
            state_icon = '🟡 Draft'
        elif pr_state == 'open':
            state_icon = '🟢 Open'
        elif pr_state == 'closed' and not pr_merged:
            state_icon = '🔴 Closed'
        else:
            state_icon = '⚫ Unknown'

        print(f"PR State: {state_icon}")
        print(f"* Title: **{pr_title}**, {pr_html_url}")

        # Blockers for open PRs
        if state_icon == '🟢 Open':
            print(f"* Blockers:")
            blockers = []
            if pr_mergeable is False:
                blockers.append('Needs rebase')
            if pr['requested_reviewers']:
                reviewers = ', '.join([u['login'] for u in pr['requested_reviewers']])
                blockers.append(f'Waiting for review from {reviewers}')
            if not blockers:
                blockers.append('Waiting for merge')
            print('  ' + ', '.join(blockers))

        # Summary line
        summary_status = 'Merged' if pr_merged else 'Mergeable' if pr_mergeable else 'Not Mergeable'
        stale_text = ' (Stale)' if pr_is_stale and state_icon == '🟢 Open' else ''
        print(f"* Summary: Short summary of the PR under 50 words, {summary_status}{stale_text}")

        # Conversations
        issue_comments = get_issue_comments(pr_number)
        review_comments = get_review_comments(pr_number)
        all_comments = issue_comments + review_comments
        insights = summarize_conversations(all_comments)
        print(f"* Conversations:")
        for insight in insights:
            print(f"  - {insight}")

        print()  # Add space between PRs

if __name__ == '__main__':
    generate_report()
