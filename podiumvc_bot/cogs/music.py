import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# yt-dlp 設定
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',  # 検索ワードをYouTubeで探す
    'noplaylist': True,
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# ffmpeg オプション
ffmpeg_options = {
    'options': '-vn'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.looping = False
        self.current_audio_url = None
        self.current_title = None

    # =====================
    # /join
    # =====================
    @app_commands.command(name="join", description="ボイスチャンネルに接続します")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("VCに参加してから実行してください。", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc is None:
            await channel.connect(timeout=30, reconnect=True)
            await interaction.response.send_message(f"VCに接続しました：{channel.name}")
        elif vc.channel != channel:
            await vc.move_to(channel)
            await interaction.response.send_message(f"VCを移動しました：{channel.name}")
        else:
            await interaction.response.send_message("すでにVCに接続しています。", ephemeral=True)

    # =====================
    # /play
    # =====================
    @app_commands.command(name="play", description="YouTubeまたはSpotifyの曲を再生します")
    @app_commands.describe(query="URLまたは検索ワードを入力")
    async def play(self, interaction: discord.Interaction, query: str):
        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message("先に /join でVCに参加してください。", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            info = ytdl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]

            audio_url = info["url"]
            title = info.get("title", "タイトル不明")

            self.current_audio_url = audio_url
            self.current_title = title
            self.looping = False

            def after_playing(err):
                if err:
                    print(f"再生エラー: {err}")
                elif self.looping and self.current_audio_url:
                    vc.play(discord.FFmpegPCMAudio(self.current_audio_url, **ffmpeg_options), after=after_playing)

            if vc.is_playing():
                vc.stop()
            vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_playing)

            await interaction.followup.send(f"🎶 再生中: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"⚠️ 再生に失敗しました: {e}")

    # =====================
    # /stop
    # =====================
    @app_commands.command(name="stop", description="再生を停止します")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            self.looping = False
            self.current_audio_url = None
            self.current_title = None
            vc.stop()
            await interaction.response.send_message("⏹️ 再生を停止しました。")
        else:
            await interaction.response.send_message("再生中の音楽がありません。", ephemeral=True)

    # =====================
    # /pause
    # =====================
    @app_commands.command(name="pause", description="一時停止")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ 一時停止しました。")
        else:
            await interaction.response.send_message("再生中の音楽がありません。", ephemeral=True)

    # =====================
    # /resume
    # =====================
    @app_commands.command(name="resume", description="再開")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ 再開しました。")
        else:
            await interaction.response.send_message("一時停止中ではありません。", ephemeral=True)

    # =====================
    # /loop
    # =====================
    @app_commands.command(name="loop", description="再生中の曲をループします")
    async def loop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            await interaction.response.send_message("再生中の音楽がありません。", ephemeral=True)
            return

        self.looping = not self.looping
        await interaction.response.send_message("🔁 ループON" if self.looping else "⏹️ ループOFF")

    # =====================
    # /leave
    # =====================
    @app_commands.command(name="leave", description="VCから切断します")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            self.looping = False
            self.current_audio_url = None
            self.current_title = None
            await vc.disconnect()
            await interaction.response.send_message("VCから切断しました。")
        else:
            await interaction.response.send_message("VCに接続していません。", ephemeral=True)


# ★ setup は必ずクラス外
async def setup(bot):
    await bot.add_cog(Music(bot))