import discord
from discord import app_commands
from discord.ext import commands
from manager import player_data as user_data

# 管理者IDセット
ADMIN_IDS = {988705655630221313}

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

class CoinCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="coin", description="自分のコイン残高を確認します")
    async def check_coins(self, interaction: discord.Interaction):
        coins = user_data.get_coins(interaction.user.id)

        embed = discord.Embed(
            title="🎫 コイン残高",
            description=f"{interaction.user.mention} さんの所持コインは **{coins}** 枚です。",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="givecoin" \
    "", description="他ユーザーにコインを送ります")
    @app_commands.describe(target="送り先のユーザー", amount="送るコインの枚数")
    async def send_coins(self, interaction: discord.Interaction, target: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ 入力エラー",
                description="送るコインは1以上で指定してください。",
                color=discord.Color.red()
            ), ephemeral=True)
            return

        sender_id = interaction.user.id
        receiver_id = target.id

        if user_data.get_coins(sender_id) < amount:
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ コイン不足",
                description="あなたのコインが足りません。",
                color=discord.Color.red()
            ), ephemeral=True)
            return

        user_data.remove_coins(sender_id, amount)
        user_data.add_coins(receiver_id, amount)

        embed = discord.Embed(
            title="✅ コイン送信完了",
            description=f"{interaction.user.mention} さんから {target.mention} さんへコインを **{amount}** 枚送りました。",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addcoin", description="管理者専用：指定ユーザーのコインを増やします")
    @app_commands.describe(target="コインを増やすユーザー", amount="増やすコインの枚数")
    async def add_coins(self, interaction: discord.Interaction, target: discord.Member, amount: int):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ 権限エラー",
                description="管理者のみ使用可能です。",
                color=discord.Color.red()
            ), ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ 入力エラー",
                description="増やすコインは1以上で指定してください。",
                color=discord.Color.red()
            ), ephemeral=True)
            return
        
        user_data.add_coins(target.id, amount)

        embed = discord.Embed(
            title="✅ コイン増加完了",
            description=f"{target.mention} のコインを {amount} 枚増やしました。",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"操作実行者: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removecoin", description="管理者専用：指定ユーザーのコインを減らします")
    @app_commands.describe(target="コインを減らすユーザー", amount="減らすコインの枚数")
    async def remove_coins(self, interaction: discord.Interaction, target: discord.Member, amount: int):
        if not is_admin(interaction.user.id):
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ 権限エラー",
                description="管理者のみ使用可能です。",
                color=discord.Color.red()
            ), ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ 入力エラー",
                description="減らすコインは1以上で指定してください。",
                color=discord.Color.red()
            ), ephemeral=True)
            return
        
        success = user_data.remove_coins(target.id, amount)
        if success:
            embed = discord.Embed(
                title="✅ コイン減少完了",
                description=f"{target.mention} のコインを {amount} 枚減らしました。",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ コイン不足",
                description=f"{target.mention} のコインは {amount} 枚以上ありません。",
                color=discord.Color.red()
            )
        embed.set_footer(text=f"操作実行者: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CoinCommands(bot))
