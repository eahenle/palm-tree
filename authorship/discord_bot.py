# discord_bot.py
import os
import discord
from .llama_agent import handle_pr_request
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    if content.lower().startswith("!lgtm"):
        await message.channel.send("✅ Merge command received. Merging PR...")
        from publishing.github_utils import merge_pr_from_context
        result = merge_pr_from_context()
        await message.channel.send(result)

    elif "review pr" in content.lower():
        try:
            pr_number = int(content.lower().split("pr")[1].strip().split()[0])
            await message.channel.send(f"🔍 Reviewing PR #{pr_number}...")
            reply = handle_pr_request(pr_number)
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"⚠️ Failed to review PR: {e}")

client.run(TOKEN)
