import json
import os
import time
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # format: "username/repo"
DISCORD_URL = os.getenv("DISCORD_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "changeme")


def get_ngrok_url():
    try:
        resp = requests.get("http://localhost:4040/api/tunnels")
        resp.raise_for_status()
        tunnels = resp.json().get("tunnels", [])
        for t in tunnels:
            if t["proto"] == "https":
                return t["public_url"]
    except Exception as e:
        print(f"Error getting ngrok URL: {e}")
    return None


def post_to_discord(url):
    if not DISCORD_URL:
        return
    content = f"🔗 Ngrok tunnel is live: {url}"
    try:
        requests.post(DISCORD_URL, json={"content": content})
    except Exception as e:
        print(f"Error posting to Discord: {e}")


def update_github_webhook(public_url):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("Missing GitHub credentials.")
        return
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    # Step 1: Get current webhooks
    hooks_url = f"https://api.github.com/repos/{GITHUB_REPO}/hooks"
    hooks_resp = requests.get(hooks_url, headers=headers)
    if hooks_resp.status_code != 200:
        print(f"Failed to get webhooks: {hooks_resp.text}")
        return

    hooks = hooks_resp.json()
    matching_hooks = [h for h in hooks if h["config"].get("url", "").endswith("/")]
    if not matching_hooks:
        print("No matching GitHub webhook found.")
        return

    webhook = matching_hooks[0]  # pick first match
    hook_id = webhook["id"]

    # Step 2: Update the webhook URL
    patch_url = f"https://api.github.com/repos/{GITHUB_REPO}/hooks/{hook_id}"
    data = {
        "config": {
            "url": f"{public_url}/",
            "content_type": "json",
            "secret": WEBHOOK_SECRET,
            "insecure_ssl": "0",
        }
    }
    patch_resp = requests.patch(patch_url, headers=headers, json=data)
    if patch_resp.status_code == 200:
        print(f"✅ GitHub webhook updated to {public_url}/")
    else:
        print(f"❌ Failed to update webhook: {patch_resp.text}")


if __name__ == "__main__":
    time.sleep(5)
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        post_to_discord(ngrok_url)
        update_github_webhook(ngrok_url)
