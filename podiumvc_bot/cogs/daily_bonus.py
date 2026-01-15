import discord
from discord import app_commands
from discord.ext import commands
from manager import player_data

class DailyBonus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="1日1回、20コインを獲得できます")
    async def daily_bonus(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        embed = discord.Embed(title="🎁 デイリーボーナス", color=discord.Color.gold())

        if player_data.claim_daily(user_id):
            embed.description = f"{interaction.user.mention} さん、デイリーボーナスで**20コイン**を獲得しました！"
        else:
            embed.description = f"{interaction.user.mention} さん、今日はすでにデイリーボーナスを受け取っています。\n明日また来てね！"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DailyBonus(bot))
