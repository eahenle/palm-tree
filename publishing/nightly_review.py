from github import Github
from .notifier import send_email, send_discord_message
from config import GITHUB_REPO, GITHUB_TOKEN

gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(GITHUB_REPO)


def main():
    pulls = repo.get_pulls(state="closed")
    for pr in pulls:
        if pr.merged and not pr.body.endswith("<!--notified-->"):
            title = pr.title
            url = pr.html_url
            summary = f"📝 Blog post merged: **{title}**\n{url}"

            send_email(f"New Blog Post: {title}", summary)
            send_discord_message(summary)

            # Mark PR as notified
            pr.edit(body=pr.body + "\n\n<!--notified-->")


if __name__ == "__main__":
    main()
