from github import Github
from agentic_blog_bot.config import GITHUB_REPO, GITHUB_TOKEN
from agentic_blog_bot.notifier import (
    send_email,
    send_discord_message,
    summarize_blog_post,
)
import re

def extract_markdown_files_from_diff(pr) -> dict:
    files = pr.get_files()
    return {
        f.filename: repo.get_contents(f.filename, ref=pr.merge_commit_sha).decoded_content.decode()
        for f in files if f.filename.endswith(".md")
    }

gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(GITHUB_REPO)

def main():
    pulls = repo.get_pulls(state="closed")
    for pr in pulls:
        if pr.merged and not pr.body.endswith("<!--notified-->"):
            title = pr.title
            url = pr.html_url

            md_files = extract_markdown_files_from_diff(pr)
            combined_content = "\n\n".join(md_files.values())

            summary = summarize_blog_post(combined_content, title)

            email_msg = f"📝 Blog post published: **{title}**\n{url}\n\nSummary:\n{summary}"
            send_email(f"New Blog Post: {title}", email_msg)
            send_discord_message(email_msg)

            # Add pre-formatted LinkedIn text
            linkedin_draft = (
                f"🚀 New blog post: {title}\n\n{summary}\n\nRead it here: {url}"
            )
            pr.create_issue_comment(f"💼 LinkedIn draft:\n\n```\n{linkedin_draft}\n```")

            pr.edit(body=pr.body + "\n\n<!--notified-->")

if __name__ == "__main__":
    main()
from agentic_blog_bot.linkedin_poster import post_to_linkedin

# Inside the PR merge block:
post_to_linkedin(summary, title, url)
