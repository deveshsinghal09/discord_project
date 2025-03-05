import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import google.generativeai as genai
import youtube_dl
import json
from datetime import datetime, timedelta
import asyncio

# environment variables from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Bot setup with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # For welcome messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Store reminders in a JSON file
REMINDERS_FILE = "reminders.json"
if not os.path.exists(REMINDERS_FILE):
    with open(REMINDERS_FILE, "w") as f:
        json.dump([], f)

# Music queue
MUSIC_QUEUE = []
QUEUE_FILE = "queue.txt"
if not os.path.exists(QUEUE_FILE):
    with open(QUEUE_FILE, "w") as f:
        f.write("")        

ydl_opts = {
    "format": "bestaudio",
    "noplaylist": True,
    "quiet": True,
}

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_reminders.start()  # Start the reminder check loop

# Event: Welcome new members
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome, {member.mention}! Enjoy your stay!")

# Chat: Respond using Gemini API
@bot.command(name="chat")
async def chat(ctx, *, message):
    try:
        response = model.generate_content(message)
        await ctx.send(response.text[:2000])  # Discord message limit
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")        


