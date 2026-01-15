import discord
from discord.ext import commands
import os
from dotenv import load_dotenv  # 追加

# .env を読み込む
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # .env の値を取得

# Intent 設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 起動イベント
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# コグのロード
import asyncio
import os

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

asyncio.run(load_cogs())

# Bot 起動
bot.run(TOKEN)
