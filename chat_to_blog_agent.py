# Agentic Blog Drafting Pipeline with GitHub PR Integration

import os, json, asyncio, datetime, subprocess, uuid, requests
from pathlib import Path
from typing import List, Set
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# === Configuration ===
CHAT_EXPORT_PATH = Path("./chat_exports")
PROCESSED_IDS_PATH = Path("./processed_chat_ids.json")
CHAT_EXPORT_PATH.mkdir(parents=True, exist_ok=True)
PROCESSED_IDS_PATH.touch(exist_ok=True)
llm = ChatOpenAI(temperature=0.7, model="gpt-4-turbo")

# GitHub settings
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "your-username/your-github-io-repo"
BASE_BRANCH = "main"
BLOG_REPO_DIR = Path("./jekyll_blog_repo")
POSTS_DIR = BLOG_REPO_DIR / "_posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)


def git_run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True)

def create_branch_and_commit_post(repo_dir: Path, filename: str, content: str):
    branch_name = f"post/{datetime.datetime.now().strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:6]}"
    git_run(["git", "checkout", "-b", branch_name], cwd=repo_dir)

    post_path = repo_dir / "_posts" / filename
    post_path.write_text(content, encoding="utf-8")

    git_run(["git", "add", str(post_path)], cwd=repo_dir)
    git_run(["git", "commit", "-m", f"Add blog post: {filename}"], cwd=repo_dir)
    git_run(["git", "push", "--set-upstream", "origin", branch_name], cwd=repo_dir)

    return branch_name



def open_pull_request(
    repo: str,
    head_branch: str,
    base_branch: str,
    github_token: str,
    post_title: str
):
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"Bearer {github_token}"}
    data = {
        "title": f"New blog post: {post_title}",
        "head": head_branch,
        "base": base_branch,
        "body": f"This PR adds a new blog post titled: **{post_title}**"
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Pull request created: {response.json()['html_url']}")



# === Chat Downloading ===
def load_processed_ids() -> Set[str]:
    if PROCESSED_IDS_PATH.exists():
        try:
            return set(json.loads(PROCESSED_IDS_PATH.read_text()))
        except json.JSONDecodeError:
            return set()
    return set()


def save_processed_ids(ids: Set[str]):
    PROCESSED_IDS_PATH.write_text(json.dumps(sorted(ids), indent=2))


def download_chatgpt_chats(destination: Path, processed_ids: Set[str]) -> List[str]:
    print("Downloading recent ChatGPT chats...")
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_SESSION_TOKEN')}"}
    url = "https://chat.openai.com/backend-api/conversations?offset=0&limit=50"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    conversations = response.json().get("items", [])

    new_ids = []
    for convo in conversations:
        convo_id = convo.get("id")
        if convo_id in processed_ids:
            continue

        convo_url = f"https://chat.openai.com/backend-api/conversation/{convo_id}"
        convo_response = requests.get(convo_url, headers=headers)
        if convo_response.status_code == 200:
            file_path = destination / f"{convo_id}.json"
            file_path.write_text(convo_response.text)
            new_ids.append(convo_id)
        else:
            print(f"Warning: Failed to fetch conversation {convo_id}")

    return new_ids


# === Chat Parsing ===
def load_recent_chats(limit=None) -> List[dict]:
    files = sorted(CHAT_EXPORT_PATH.glob("*.json"), key=os.path.getmtime, reverse=True)
    if limit:
        files = files[:limit]
    return [json.loads(f.read_text()) for f in files]


def extract_ideas_from_chat(chat: dict) -> List[str]:
    messages = chat.get("mapping", {})
    contents = []
    for entry in messages.values():
        msg = entry.get("message", {})
        if not msg:
            continue
        role = msg.get("author", {}).get("role")
        content = msg.get("content", {}).get("parts", [""])[0]
        contents.append(f"{role}: {content}")
    transcript = "\n".join(contents)

    prompt = [
        HumanMessage(
            content=f"""
        Analyze the following ChatGPT conversation and extract 3 distinct, interesting ideas that could form the basis of technical or reflective blog posts:

        {transcript}
        """
        )
    ]
    response = llm(prompt)
    ideas = response.content.strip().split("\n")
    return [idea.strip("- ").strip() for idea in ideas if idea.strip()]


def generate_blog_draft(idea: str) -> str:
    prompt = [
        HumanMessage(
            content=f"""
        Write a detailed, informative blog post based on this idea:

        "{idea}"

        The blog post should include an engaging introduction, several structured sections, and a thoughtful conclusion. Aim for a professional yet conversational tone.
        """
        )
    ]
    response = llm(prompt)
    return response.content.strip()


def save_draft_to_jekyll(idea: str, content: str, category="chatgpt", tags=None):
    if tags is None:
        tags = ["ai", "automation", "chatgpt"]

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S %z")

    # Create slug-safe title
    slug = "-".join(idea.lower().split()[:6])
    slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)
    filename = f"{date_str}-{slug}.md"

    post_path = Path("../your-jekyll-site/_posts/") + filename

    front_matter = f"""---
        layout: post
        title: "{idea}\
        date: {now.strftime('%Y-%m-%d %H:%M:%S')} -0700
        categories: [{category}]
        tags: [{', '.join(tags)}]
        ---

        """

    post_content = front_matter + "\n" + content.strip()

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(post_content)

    print(f"Saved post to: {post_path}")


# === Main Agent Flow ===
async def run_agent():
    processed_ids = load_processed_ids()
    new_ids = download_chatgpt_chats(CHAT_EXPORT_PATH, processed_ids)

    if not new_ids:
        print("No new chats to process.")
        return

    chats = load_recent_chats()
    for chat in chats:
        if chat.get("id") not in new_ids:
            continue
        ideas = extract_ideas_from_chat(chat)
        for idea in ideas:
            blog_post = generate_blog_draft(idea)
            filename, content = save_draft_to_jekyll(idea, blog_post)
            branch = create_branch_and_commit_post(filename, content)
            open_pull_request(REPO, branch, BASE_BRANCH, GITHUB_TOKEN, idea)

    processed_ids.update(new_ids)
    save_processed_ids(processed_ids)


if __name__ == "__main__":
    asyncio.run(run_agent())
