import smtplib
from email.message import EmailMessage
import os
import requests

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_email(subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
        print(f"📧 Email sent: {subject}")


def send_discord_message(content: str):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Discord webhook not set")
        return

    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    if response.ok:
        print("✅ Discord notification sent")
    else:
        print(f"❌ Discord webhook error: {response.text}")


from config import OPENAI_API_KEY
import openai


def summarize_blog_post(post_content: str, pr_title: str) -> str:
    prompt = f"""Summarize the following blog post titled '{pr_title}' in 1–3 sentences for a general audience. Highlight why it’s interesting or useful. Keep it friendly and professional.

Blog post:
{post_content}
"""

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
