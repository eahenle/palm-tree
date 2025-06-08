import os
import requests

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
ISSUE_TITLE = "🚫 ChatGPT Login Expired - Refresh Needed"
ISSUE_BODY = """
The `auth.json` session used to authenticate with ChatGPT has expired.

To restore functionality:
1. Run `playwright codegen https://chat.openai.com/`
2. Save the session state to `auth.json`
3. Commit or securely upload it to the workflow

This issue was created automatically by the blog agent pipeline.
"""

def issue_exists():
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/issues",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        params={"state": "open"}
    )
    return any(ISSUE_TITLE in issue["title"] for issue in r.json())

def create_issue():
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/issues",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        json={"title": ISSUE_TITLE, "body": ISSUE_BODY}
    )
    print(f"Issue created: {r.json().get('html_url')}")

if __name__ == "__main__":
    if not issue_exists():
        create_issue()
