import discord
import json
import os
from pathlib import Path
import subprocess

# === CONFIGURATION ===
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("DISCORD_USER_ID", "0"))  # your personal Discord ID
SAVE_PATH = "auth.json"  # where to save the updated session

# Optional: auto-trigger GitHub Action after auth.json update
TRIGGER_DEPLOY = os.getenv("TRIGGER_GITHUB_ACTION", "false").lower() == "true"
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")  # e.g. "username/blog-repo"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TRIGGER_WORKFLOW = os.getenv(
    "GITHUB_WORKFLOW_FILE", ".github/workflows/draft-from-chat.yml"
)

intents = discord.Intents.default()
intents.message_content = True  # Important for reading message content
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author.bot or message.author.id != ALLOWED_USER_ID:
        return

    if message.content.startswith("!update-auth"):
        try:
            payload = message.content[len("!update-auth") :].strip()
            auth_data = json.loads(payload)  # raises if not valid JSON

            # Save new auth.json
            Path(SAVE_PATH).write_text(json.dumps(auth_data, indent=2))
            await message.channel.send("✅ `auth.json` updated successfully.")

            # Optional: trigger GitHub Action
            if TRIGGER_DEPLOY:
                triggered = trigger_github_action()
                await message.channel.send(
                    "🚀 GitHub Action triggered."
                    if triggered
                    else "⚠️ Could not trigger GitHub Action."
                )

        except Exception as e:
            await message.channel.send(f"❌ Failed to update: {e}")


def trigger_github_action():
    """Trigger a GitHub Actions workflow_dispatch event"""
    if not (GITHUB_REPO and GITHUB_TOKEN):
        return False

    r = subprocess.run(
        [
            "curl",
            "-X",
            "POST",
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{TRIGGER_WORKFLOW}/dispatches",
            "-H",
            f"Authorization: token {GITHUB_TOKEN}",
            "-H",
            "Accept: application/vnd.github.v3+json",
            "-d",
            '{"ref":"main"}',
        ],
        capture_output=True,
    )

    return r.returncode == 0


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN or not ALLOWED_USER_ID:
        print("❌ You must set DISCORD_BOT_TOKEN and DISCORD_USER_ID")
        exit(1)

    client.run(DISCORD_BOT_TOKEN)
