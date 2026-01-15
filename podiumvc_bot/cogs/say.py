import discord
from discord.ext import commands
from discord import app_commands
import os

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_folder = "voice"  # mp3ファイル置き場

    @app_commands.command(
        name="say", 
        description="用意した音声ファイル(mp3)を再生します"
    )
    @app_commands.describe(
        voice_name="再生したい音声を選択してください"
    )
    @app_commands.choices(
        voice_name=[
            app_commands.Choice(name="めぐみん", value="line1"),
            app_commands.Choice(name="サンズ", value="line2"),
            app_commands.Choice(name="コナン", value="line3"),
            app_commands.Choice(name="ニカ", value="line4"),
            app_commands.Choice(name="呪術回線", value="line5"),
            app_commands.Choice(name="秤", value="line6"),
            app_commands.Choice(name="ペルソナ", value="line7"),
            app_commands.Choice(name="シャドウ", value="line8"),
            app_commands.Choice(name="ベニマル", value="line9"),
            app_commands.Choice(name="ブルーロック", value="line10"),
        ]
    )
    async def say(self, interaction: discord.Interaction, voice_name: app_commands.Choice[str]):
        file_path = os.path.join(self.voice_folder, f"{voice_name.value}.mp3")

        # ファイルが存在するか確認
        if not os.path.isfile(file_path):
            await interaction.response.send_message(
                "❌ 音声ファイルが見つかりません。", ephemeral=True
            )
            return

        # VCに接続しているか確認
        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message(
                "❌ 先に /join でVCに接続してください。", ephemeral=True
            )
            return

        await interaction.response.defer()  # 遅延応答

        # 再生中なら停止
        if vc.is_playing():
            vc.stop()

        # 音声再生
        vc.play(discord.FFmpegPCMAudio(source=file_path))

        await interaction.followup.send(
            f"🎧 「{voice_name.name}」を再生します。"
        )


# ★ setup は必ず Cog 外
async def setup(bot):
    await bot.add_cog(Say(bot))
