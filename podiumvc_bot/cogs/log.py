import discord
from discord.ext import commands

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # メッセージ削除イベント
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return  # Botのメッセージは無視

        embed = discord.Embed(
            title="💬 メッセージ削除",
            description=message.content or "[画像・添付のみ]",
            color=discord.Color.red()
        )
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.add_field(name="チャンネル", value=message.channel.mention)
        if message.attachments:
            urls = "\n".join(att.url for att in message.attachments)
            embed.add_field(name="添付ファイル", value=urls, inline=False)

        await self.send_log(embed)

    # メッセージ編集イベント
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return  # Botメッセージは無視
        if before.content == after.content:
            return  # 内容が変わらなければ無視

        embed = discord.Embed(
            title="✏️ メッセージ編集",
            color=discord.Color.orange()
        )
        embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.add_field(name="チャンネル", value=before.channel.mention)
        embed.add_field(name="変更前", value=before.content or "[画像・添付のみ]", inline=False)
        embed.add_field(name="変更後", value=after.content or "[画像・添付のみ]", inline=False)

        await self.send_log(embed)

    # Bot自身にDMで送信
    async def send_log(self, embed):
        bot_user = self.bot.user
        try:
            await bot_user.send(embed=embed)
        except Exception as e:
            print(f"DM送信失敗: {e}")

# CogをBotに追加
async def setup(bot):
    await bot.add_cog(Logger(bot))
