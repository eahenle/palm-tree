import os
import json
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback")
TOKEN_FILE = ".agent_cache/linkedin_token.json"

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

SCOPE = "w_member_social"


def get_authorization_url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "DCEEFWF45453sdffef424",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def fetch_access_token(auth_code):
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    data = response.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)
    return data["access_token"]


def load_access_token():
    if not os.path.exists(TOKEN_FILE):
        print("🔑 LinkedIn token missing. Visit this URL to authenticate:")
        print(get_authorization_url())
        return None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    return data["access_token"]


def post_to_linkedin(summary: str, title: str, url: str):
    token = load_access_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    profile_res = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    user_id = profile_res.json().get("id")

    hashtags = ["AI", "Python", "Blogging", "MachineLearning"]
    tag_str = " ".join(f"#{tag}" for tag in hashtags)

    post_body = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"🚀 New blog post: {title}\n\n{summary}\n\nRead it here: {url}\n\n{tag_str}"
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    post_res = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={**headers, "Content-Type": "application/json"},
        json=post_body,
    )

    if post_res.status_code == 201:
        print("✅ LinkedIn post published!")
    else:
        print("❌ Failed to post:", post_res.text)
