import os
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

CHAT_DIR = Path("chat_exports")
PROCESSED_RECORD = Path("processed_chats.json")
CHAT_LIST_URL = "https://chat.openai.com/backend-api/conversations"

def load_processed_ids():
    if PROCESSED_RECORD.exists():
        return set(json.loads(PROCESSED_RECORD.read_text()))
    return set()

def save_processed_ids(ids):
    PROCESSED_RECORD.write_text(json.dumps(sorted(list(ids)), indent=2))

async def fetch_chatgpt_chats():
    CHAT_DIR.mkdir(exist_ok=True)
    processed_ids = load_processed_ids()
    new_ids = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="auth.json")  # Assumes you're already logged in
        page = await context.new_page()

        # Get token
        await page.goto("https://chat.openai.com/")
        session = await page.evaluate("""() => {
            return fetch("/api/auth/session").then(r => r.json());
        }""")
        token = session["accessToken"]

        # Fetch conversations
        headers = {"Authorization": f"Bearer {token}"}
        await page.goto(CHAT_LIST_URL, wait_until="networkidle")
        response = await page.evaluate(f"""() => {{
            return fetch("{CHAT_LIST_URL}", {{
                headers: {{
                    Authorization: "Bearer {token}"
                }}
            }}).then(r => r.json());
        }}""")

        for convo in response.get("items", []):
            cid = convo["id"]
            if cid in processed_ids:
                continue
            filename = CHAT_DIR / f"{cid}.json"
            filename.write_text(json.dumps(convo, indent=2))
            new_ids.add(cid)

        await browser.close()

    if new_ids:
        processed_ids.update(new_ids)
        save_processed_ids(processed_ids)

    print(f"Downloaded {len(new_ids)} new chats.")

if __name__ == "__main__":
    asyncio.run(fetch_chatgpt_chats())
