import json
import requests
import time
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_URL")  # set this in .env

def get_ngrok_url():
    try:
        resp = requests.get("http://localhost:4040/api/tunnels")
        resp.raise_for_status()
        tunnels = resp.json().get("tunnels", [])
        for t in tunnels:
            if t["proto"] == "https":
                return t["public_url"]
    except Exception as e:
        print(f"Error: {e}")
    return None

def post_to_discord(url):
    content = f"🔗 Ngrok tunnel is live: {url}"
    requests.post(DISCORD_WEBHOOK_URL, json={"content": content})

if __name__ == "__main__":
    time.sleep(5)  # wait a few seconds for ngrok to start
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        post_to_discord(ngrok_url)
    else:
        print("❌ Could not find Ngrok URL.")
