# check_auth.py
import asyncio
from playwright.async_api import async_playwright

async def is_login_valid() -> bool:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="auth.json")
        page = await context.new_page()

        try:
            await page.goto("https://chat.openai.com/")
            result = await page.evaluate("""() =>
                fetch("/api/auth/session").then(r => r.ok)
            """)
        except Exception as e:
            print(f"Error during login check: {e}")
            return False
        finally:
            await browser.close()

        return result

if __name__ == "__main__":
    result = asyncio.run(is_login_valid())
    if not result:
        print("❌ Login invalid. Please refresh `auth.json` via `playwright codegen`.")
        exit(1)
    else:
        print("✅ Login is valid.")
