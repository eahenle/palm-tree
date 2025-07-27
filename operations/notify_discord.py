import os
import requests

webhook_url = os.getenv("DISCORD_WEBHOOK")
repo_url = f"https://github.com/{os.getenv('GITHUB_REPOSITORY')}"
issue_title = "🚫 ChatGPT Login Expired - Refresh Needed"
search_url = (
    f"{repo_url}/issues?q=is%3Aissue+is%3Aopen+{requests.utils.quote(issue_title)}"
)

message = {
    "content": (
        "⚠️ **ChatGPT login expired**\n"
        "The `auth.json` session is no longer valid.\n\n"
        f"🔗 [GitHub Repository]({repo_url})\n"
        f"📌 [Open Issue]({search_url})\n\n"
        "**Please refresh it:**\n"
        "```bash\nplaywright codegen https://chat.openai.com\n```\n"
        "Then upload the new `auth.json`."
    )
}

if webhook_url:
    r = requests.post(webhook_url, json=message)
    if r.ok:
        print("✅ Sent Discord alert")
    else:
        print(f"❌ Discord webhook failed: {r.status_code} - {r.text}")
else:
    print("❌ DISCORD_WEBHOOK not set")
