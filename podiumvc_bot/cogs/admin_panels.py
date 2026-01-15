import discord
from discord.ext import commands
from discord import app_commands

class AdminPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================
    # /kick
    # =====================
    @app_commands.command(name="kick", description="選択したメンバーをキックします")
    @app_commands.describe(members="キックするメンバーを選択")
    async def kick(self, interaction: discord.Interaction, members: str):
        await interaction.response.defer()
        member_ids = [int(m.strip("<@!>")) for m in members.split(",")]
        guild = interaction.guild
        kicked_members = []

        for member_id in member_ids:
            member = guild.get_member(member_id)
            if member:
                try:
                    await member.kick(reason=f"管理パネル操作 by {interaction.user}")
                    kicked_members.append(member.name)
                except Exception as e:
                    print(f"Kick error: {e}")

        embed = discord.Embed(
            title="⚠️ キック結果",
            description="キックされたメンバー: " + ", ".join(kicked_members) if kicked_members else "対象なし",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

    # =====================
    # /ban
    # =====================
    @app_commands.command(name="ban", description="選択したメンバーをBANします")
    @app_commands.describe(members="BANするメンバーを選択")
    async def ban(self, interaction: discord.Interaction, members: str):
        await interaction.response.defer()
        member_ids = [int(m.strip("<@!>")) for m in members.split(",")]
        guild = interaction.guild
        banned_members = []

        for member_id in member_ids:
            member = guild.get_member(member_id)
            if member:
                try:
                    await member.ban(reason=f"管理パネル操作 by {interaction.user}")
                    banned_members.append(member.name)
                except Exception as e:
                    print(f"Ban error: {e}")

        embed = discord.Embed(
            title="⛔ BAN結果",
            description="BANされたメンバー: " + ", ".join(banned_members) if banned_members else "対象なし",
            color=discord.Color.dark_red()
        )
        await interaction.followup.send(embed=embed)

    # =====================
    # /timeout
    # =====================
    @app_commands.command(name="timeout", description="選択したメンバーをタイムアウトします")
    @app_commands.describe(members="タイムアウトするメンバーを選択", duration="秒単位でタイムアウト時間")
    async def timeout(self, interaction: discord.Interaction, members: str, duration: int):
        await interaction.response.defer()
        member_ids = [int(m.strip("<@!>")) for m in members.split(",")]
        guild = interaction.guild
        timed_out_members = []

        for member_id in member_ids:
            member = guild.get_member(member_id)
            if member:
                try:
                    await member.timeout(duration=discord.utils.utcnow() + discord.timedelta(seconds=duration))
                    timed_out_members.append(member.name)
                except Exception as e:
                    print(f"Timeout error: {e}")

        embed = discord.Embed(
            title="⏳ タイムアウト結果",
            description="タイムアウトされたメンバー: " + ", ".join(timed_out_members) if timed_out_members else "対象なし",
            color=discord.Color.orange()
        )
        await interaction.followup.send(embed=embed)

    # =====================
    # /role_create
    # =====================
    @app_commands.command(name="role_create", description="新しいロールを作成します")
    @app_commands.describe(role_name="作成するロール名", color="ロールカラー(例: red, blue, green)")
    async def role_create(self, interaction: discord.Interaction, role_name: str, color: str = "default"):
        await interaction.response.defer()
        guild = interaction.guild
        try:
            color_dict = {
                "red": discord.Color.red(),
                "green": discord.Color.green(),
                "blue": discord.Color.blue(),
                "yellow": discord.Color.yellow(),
                "default": discord.Color.default()
            }
            role = await guild.create_role(name=role_name, color=color_dict.get(color.lower(), discord.Color.default()))
            embed = discord.Embed(
                title="✅ ロール作成",
                description=f"作成されたロール: {role.name}",
                color=role.color
            )
        except Exception as e:
            embed = discord.Embed(
                title="❌ エラー",
                description=f"ロール作成に失敗しました: {e}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

    # =====================
    # /role_assign
    # =====================
    @app_commands.command(name="role_assign", description="選択したメンバーにロールを付与します")
    @app_commands.describe(members="対象メンバー（@で複数可）", role="付与するロール")
    async def role_assign(self, interaction: discord.Interaction, members: str, role: discord.Role):
        await interaction.response.defer()
        member_ids = [int(m.strip("<@!>")) for m in members.split(",")]
        assigned = []

        for member_id in member_ids:
            member = interaction.guild.get_member(member_id)
            if member:
                try:
                    await member.add_roles(role)
                    assigned.append(member.name)
                except Exception as e:
                    print(f"Role assign error: {e}")

        embed = discord.Embed(
            title="✅ ロール付与結果",
            description="付与されたメンバー: " + ", ".join(assigned) if assigned else "対象なし",
            color=role.color
        )
        await interaction.followup.send(embed=embed)

    # =====================
    # /role_remove
    # =====================
    @app_commands.command(name="role_remove", description="選択したメンバーからロールを剥奪します")
    @app_commands.describe(members="対象メンバー（@で複数可）", role="剥奪するロール")
    async def role_remove(self, interaction: discord.Interaction, members: str, role: discord.Role):
        await interaction.response.defer()
        member_ids = [int(m.strip("<@!>")) for m in members.split(",")]
        removed = []

        for member_id in member_ids:
            member = interaction.guild.get_member(member_id)
            if member:
                try:
                    await member.remove_roles(role)
                    removed.append(member.name)
                except Exception as e:
                    print(f"Role remove error: {e}")

        embed = discord.Embed(
            title="✅ ロール剥奪結果",
            description="剥奪されたメンバー: " + ", ".join(removed) if removed else "対象なし",
            color=role.color
        )
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminPanel(bot))
