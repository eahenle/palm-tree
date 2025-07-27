# github_utils.py
import os
import requests
from github import Github
from pathlib import Path

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # e.g., "username/blog"
REPO = (
    Github(GITHUB_TOKEN).get_repo(GITHUB_REPO) if GITHUB_TOKEN and GITHUB_REPO else None
)

PR_CONTEXT_FILE = "/tmp/last_pr.txt"


def get_pr_diff_and_comments(pr_number: int):
    pr = get_repo().get_pull(pr_number)
    files = pr.get_files()
    comments = pr.get_review_comments()

    diff_text = "\n\n".join([f"{f.filename}:\n{f.patch or ''}" for f in files])
    comment_text = "\n\n".join([f"{c.user.login}: {c.body}" for c in comments])

    return diff_text, comment_text


def save_pr_to_local(pr_number: int, diff_text: str, comments: str) -> str:
    base_dir = Path(f"data/pr_{pr_number}")
    base_dir.mkdir(parents=True, exist_ok=True)

    with open(base_dir / "diff.md", "w") as f:
        f.write(f"# PR #{pr_number} Diff\n\n{diff_text}")

    with open(base_dir / "comments.md", "w") as f:
        f.write(f"# PR #{pr_number} Review Comments\n\n{comments}")

    with open(PR_CONTEXT_FILE, "w") as f:
        f.write(str(pr_number))

    return str(base_dir)


def merge_pr_from_context():
    if not os.path.exists(PR_CONTEXT_FILE):
        return "❌ No prior PR context found."

    with open(PR_CONTEXT_FILE) as f:
        pr_number = int(f.read().strip())

    pr = get_repo().get_pull(pr_number)
    if pr.is_merged():
        return f"🔁 PR #{pr_number} is already merged."

    if pr.mergeable:
        pr.merge(merge_method="squash", commit_message="Auto-merged by agent")
        return f"✅ Merged PR #{pr_number}"
    else:
        return f"⚠️ PR #{pr_number} is not mergeable right now."


import hashlib
import json

CACHE_PATH = Path(".agent_cache")
CACHE_PATH.mkdir(exist_ok=True)
PR_SHAS_FILE = CACHE_PATH / "pr_shas.json"


def get_cached_shas():
    if PR_SHAS_FILE.exists():
        with open(PR_SHAS_FILE) as f:
            return json.load(f)
    return {}


def update_cached_sha(pr_number: int, sha: str):
    shas = get_cached_shas()
    shas[str(pr_number)] = sha
    with open(PR_SHAS_FILE, "w") as f:
        json.dump(shas, f)


def compute_diff_sha(diff_text: str) -> str:
    return hashlib.sha256(diff_text.encode()).hexdigest()


def should_skip_review(pr_number: int, new_sha: str) -> bool:
    shas = get_cached_shas()
    return shas.get(str(pr_number)) == new_sha
