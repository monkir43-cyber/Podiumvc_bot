import random
import discord
from discord import app_commands
from discord.ext import commands
from manager import player_data  # コイン管理は共通

# ガチャで当たるロールIDまたは名前をリストで用意
GACHA_ROLES = [
    "🥇ゴールド",  # 例: サーバーに存在するロール名
    "🥈シルバー",
    "🥉ブロンズ"
]

GACHA_COST = 50  # 1回のガチャに必要なコイン

class Gacha(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="gacha", description=f"{GACHA_COST}コインでランダムロールガチャを引きます")
    async def gacha(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # コインチェック
        if player_data.get_coins(user_id) < GACHA_COST:
            await interaction.response.send_message("❌ コインが足りません。", ephemeral=True)
            return

        # コイン減らす
        player_data.remove_coins(user_id, GACHA_COST)

        # ランダムでロール決定
        role_name = random.choice(GACHA_ROLES)
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            await interaction.response.send_message(f"⚠️ ガチャロール `{role_name}` が見つかりません。", ephemeral=True)
            return

        # ロール付与
        try:
            await interaction.user.add_roles(role)
            embed = discord.Embed(
                title="🎲 ガチャ結果 🎲",
                description=f"{interaction.user.mention} さんは `{role.name}` をゲット！",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"{GACHA_COST}コイン消費")
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ ロール付与権限がありません。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ エラーが発生しました: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Gacha(bot))
