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


@bot.command(name="summarize")
async def summarize(ctx, *, message):
    try:
        prompt = f"Summarize this: {message}"
        response = model.generate_content(prompt)
        await ctx.send(f"Summary: {response.text[:2000]}")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

# Poll: Create a simple yes/no poll
@bot.command(name="poll")
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=discord.Color.blue())
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

# Reminder: Set a reminder
@bot.command(name="remind")
async def remind(ctx, time_str, *, reminder_text):
    try:
        # Parse time (e.g., "5m" for 5 minutes, "2h" for 2 hours, "1d" for 1 day)
        unit = time_str[-1].lower()
        amount = int(time_str[:-1])
        if unit == "m":
            delta = timedelta(minutes=amount)
        elif unit == "h":
            delta = timedelta(hours=amount)
        elif unit == "d":
            delta = timedelta(days=amount)
        else:
            await ctx.send("Use format: !remind 5m <text> (m=minutes, h=hours, d=days)")
            return

        remind_time = datetime.now() + delta
        reminder = {
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "text": reminder_text,
            "time": remind_time.isoformat()
        }

        # Save to file
        with open(REMINDERS_FILE, "r") as f:
            reminders = json.load(f)
        reminders.append(reminder)
        with open(REMINDERS_FILE, "w") as f:
            json.dump(reminders, f)

        await ctx.send(f"Reminder set for {remind_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except ValueError:
        await ctx.send("Invalid time format. Use: !remind 5m <text>")