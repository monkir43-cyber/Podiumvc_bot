import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="アンケートを作成します")
    @app_commands.describe(
        question="アンケートの質問",
        options="選択肢をカンマで区切って入力（最大10個）",
        duration="タイマー（秒、任意）"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        options: str,
        duration: int = 0
    ):
        await interaction.response.defer()

        # 選択肢をリスト化
        choices = [opt.strip() for opt in options.split(",")][:10]
        if len(choices) < 2:
            await interaction.followup.send("⚠️ 選択肢は最低2つ必要です。", ephemeral=True)
            return

        # 絵文字リスト（最大10個）
        emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        embed = discord.Embed(
            title="📊 アンケート",
            description=f"**{question}**",
            color=discord.Color.blue()
        )

        description = ""
        for i, choice in enumerate(choices):
            description += f"{emojis[i]} {choice}\n"
        embed.add_field(name="選択肢", value=description, inline=False)

        if duration > 0:
            embed.set_footer(text=f"締め切り: {duration}秒後")

        # 投票メッセージ送信
        poll_message = await interaction.followup.send(embed=embed)

        # リアクション追加
        for i in range(len(choices)):
            await poll_message.add_reaction(emojis[i])

        # タイマー処理
        if duration > 0:
            await asyncio.sleep(duration)
            poll_message = await interaction.channel.fetch_message(poll_message.id)

            # 投票結果集計
            result = []
            for i in range(len(choices)):
                reaction = discord.utils.get(poll_message.reactions, emoji=emojis[i])
                if reaction:
                    # botのリアクションを除く
                    count = reaction.count - 1
                else:
                    count = 0
                result.append((choices[i], count))

            # 結果Embed
            result_text = "\n".join([f"{c[0]}: {c[1]}票" for c in result])
            result_embed = discord.Embed(
                title="📊 アンケート結果",
                description=f"**{question}**\n\n{result_text}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=result_embed)


async def setup(bot):
    await bot.add_cog(Poll(bot))
