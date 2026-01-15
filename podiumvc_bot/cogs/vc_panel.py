import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

class VCPannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================
    # /vc_panel
    # =====================
    @app_commands.command(name="vc_panel", description="VCメンバーパネルを表示します")
    async def vc_panel(self, interaction: discord.Interaction):
        vc = interaction.user.voice.channel if interaction.user.voice else None
        if not vc:
            await interaction.response.send_message("先にVCに参加してください。", ephemeral=True)
            return

        embed = discord.Embed(title="VCメンバーパネル", description=f"チャンネル: {vc.name}", color=0x00ff00)
        members = "\n".join([member.display_name for member in vc.members])
        embed.add_field(name="参加メンバー", value=members or "なし", inline=False)

        view = VCPanelView(vc)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# =====================
# VC操作用ボタン
# =====================
class VCPanelView(View):
    def __init__(self, vc: discord.VoiceChannel):
        super().__init__(timeout=None)
        self.vc = vc

    @discord.ui.button(label="全員ミュート", style=discord.ButtonStyle.danger)
    async def mute_all(self, interaction: discord.Interaction, button: Button):
        if not self.vc.members:
            await interaction.response.send_message("VCにメンバーがいません。", ephemeral=True)
            return

        for member in self.vc.members:
            if member != interaction.user:  # 自分は除外可能
                try:
                    await member.edit(mute=True)
                except Exception:
                    pass
        await interaction.response.send_message("✅ 全員ミュートしました", ephemeral=True)

    @discord.ui.button(label="全員アンミュート", style=discord.ButtonStyle.success)
    async def unmute_all(self, interaction: discord.Interaction, button: Button):
        if not self.vc.members:
            await interaction.response.send_message("VCにメンバーがいません。", ephemeral=True)
            return

        for member in self.vc.members:
            if member != interaction.user:
                try:
                    await member.edit(mute=False)
                except Exception:
                    pass
        await interaction.response.send_message("✅ 全員アンミュートしました", ephemeral=True)

    @discord.ui.button(label="ボットをこのVCに移動", style=discord.ButtonStyle.primary)
    async def move_bot(self, interaction: discord.Interaction, button: Button):
        bot_member = interaction.guild.me
        vc_client = interaction.guild.voice_client
        if vc_client:
            await vc_client.move_to(self.vc)
            await interaction.response.send_message(f"🤖 ボットを {self.vc.name} に移動しました", ephemeral=True)
        else:
            await interaction.response.send_message("ボットがVCに接続していません。", ephemeral=True)


# ★ setup は必ず Cog 外
async def setup(bot):
    await bot.add_cog(VCPannel(bot))
