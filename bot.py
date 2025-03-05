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