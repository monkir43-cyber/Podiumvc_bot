import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timer", description="埋め込みでカウントダウンするタイマーをセットします")
    @app_commands.describe(time="タイマー時間（秒, 1m, 2hなど）", message="タイマー終了時に送るメッセージ（任意）")
    async def timer(self, interaction: discord.Interaction, time: str, message: str = "⏰ タイマー終了です！"):
        await interaction.response.defer()
        seconds = self.parse_time(time)
        if seconds is None or seconds <= 0:
            await interaction.followup.send("⚠️ 時間の形式が不正です。例: `10s`, `5m`, `2h`")
            return

        embed = discord.Embed(
            title="⏱️ タイマー",
            description=f"残り時間: {self.format_time(seconds)}",
            color=discord.Color.blurple()
        )
        countdown_msg = await interaction.followup.send(embed=embed)

        for remaining in range(seconds, 0, -1):
            embed.description = f"残り時間: {self.format_time(remaining)}"
            await countdown_msg.edit(embed=embed)
            await asyncio.sleep(1)

        # タイマー終了
        embed.description = f"{message}"
        embed.color = discord.Color.green()
        await countdown_msg.edit(embed=embed)

    def parse_time(self, time_str: str) -> int | None:
        """時間文字列を秒に変換"""
        try:
            if time_str.endswith("s"):
                return int(time_str[:-1])
            elif time_str.endswith("m"):
                return int(time_str[:-1]) * 60
            elif time_str.endswith("h"):
                return int(time_str[:-1]) * 3600
            else:
                return int(time_str)  # 秒として扱う
        except ValueError:
            return None

    def format_time(self, seconds: int) -> str:
        """秒を hh:mm:ss 形式に変換"""
        h, m = divmod(seconds, 3600)
        m, s = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"

async def setup(bot):
    await bot.add_cog(Timer(bot))
