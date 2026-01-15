import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import os

# 音声ファイル格納フォルダ
VOICE_FOLDER = "sounds"

# サンズ戦用音源ファイル
sans_battle_start_file = os.path.join(VOICE_FOLDER, "sans_battle_start.mp3")
sans_battle_mid_file = os.path.join(VOICE_FOLDER, "sans_battle_mid.mp3")
sans_battle_final_file = os.path.join(VOICE_FOLDER, "sans_battle_final.mp3")
sans_appearance_sound_file = os.path.join(VOICE_FOLDER, "sans_appearance.mp3")

# GIFリンク
heal_gif = "https://furiirakun.com/wp/wp-content/uploads/2021/05/165-1.gif"
debuff_gif = "https://ugokawaii.com/wp-content/uploads/2022/08/medicine-capsule.gif"
sans_appearance_gif = "https://www.icegif.com/wp-content/uploads/icegif-4050.gif"
win_gif = "https://media.tenor.com/2gcR0jU5EMEAAAAC/%E5%AC%89%E3%81%97%E3%81%84-%E3%82%84%E3%81%A3%E3%81%9F%E3%83%BC.gif"
lose_gif = "https://media1.tenor.com/m/zuTgjBHRZiQAAAAC/%E6%B3%A3%E3%81%8F-%E6%82%B2%E3%81%97%E3%81%84.gif"

sans_dialogues = [
    "君にはまだ早すぎる。",
    "戦う理由なんて、どうでもいいんだ。",
    "君が死ぬのを楽しみにしてるよ。",
    "ほんとうに戦うのか？ここまで来て、逃げないのか？"
]

def calculate_sans_damage(turn_count):
    if 1 <= turn_count <= 5:
        return random.randint(8, 12)
    elif 6 <= turn_count <= 10:
        return random.randint(12, 16)
    elif 11 <= turn_count <= 15:
        return random.randint(16, 20)
    else:
        return random.randint(20, 25)

class SansBattleView(discord.ui.View):
    def __init__(self, bot, ctx, battle):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx
        self.battle = battle

    @discord.ui.button(label="攻撃", style=discord.ButtonStyle.green)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.battle.handle_button(interaction, "attack")

    @discord.ui.button(label="行動", style=discord.ButtonStyle.blurple)
    async def action(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.battle.handle_button(interaction, "action")

    @discord.ui.button(label="アイテム", style=discord.ButtonStyle.primary)
    async def item(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.battle.handle_button(interaction, "item")

    @discord.ui.button(label="逃げる", style=discord.ButtonStyle.danger)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.battle.handle_button(interaction, "flee")


class SansBattleInstance:
    def __init__(self, bot, ctx, vc):
        self.bot = bot
        self.ctx = ctx
        self.vc = vc
        self.player_hp = 300
        self.sans_hp = 1
        self.sans_avoidance_rate = 0.99
        self.used_heal = False
        self.used_debuff = False
        self.turn_count = 0
        self.message = None
        self.joke_effect = False
        self.in_battle = True
        self.joke_active_turn = None

    async def safe_disconnect(self):
        if self.vc and self.vc.is_connected():
            try:
                await self.vc.disconnect()
            except:
                pass

    async def play_sound(self, filename):
        if not os.path.isfile(filename):
            print(f"音声ファイルが見つかりません: {filename}")
            return
        try:
            self.vc.play(discord.FFmpegPCMAudio(source=filename))
            while self.vc.is_playing():
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"音声再生エラー: {e}")
            await self.safe_disconnect()

    async def play_bgm(self, filename):
        if not os.path.isfile(filename):
            print(f"音声ファイルが見つかりません: {filename}")
            return
        try:
            if self.vc.is_playing():
                self.vc.stop()
            self.vc.play(discord.FFmpegPCMAudio(source=filename))
        except Exception as e:
            print(f"BGM再生エラー: {e}")
            await self.safe_disconnect()

    async def start(self):
        content = f"サンズが現れた！戦闘準備はいいか？\n{sans_appearance_gif}\n"
        content += random.choice(sans_dialogues)
        self.message = await self.ctx.followup.send(content=content, ephemeral=False)

        await self.play_sound(sans_appearance_sound_file)
        await self.play_bgm(sans_battle_start_file)
        await self.next_turn()

    async def next_turn(self):
        if not self.in_battle:
            return

        self.turn_count += 1

        if self.player_hp <= 0:
            await self.ctx.followup.send(f"あなたは倒された…。サンズに勝つことはできなかった…。\n{lose_gif}")
            await self.safe_disconnect()
            self.in_battle = False
            return

        if self.sans_hp <= 0:
            await self.ctx.followup.send(f"サンズを倒した！あなたの勝利！\n{win_gif}")
            await self.safe_disconnect()
            self.in_battle = False
            return

        if self.turn_count >= 20:
            await self.ctx.followup.send("時間切れ！サンズは最強の攻撃を仕掛けてきた！即死攻撃！")
            await self.ctx.followup.send(f"あなたはサンズの最終攻撃で倒された…。\n{lose_gif}")
            await self.safe_disconnect()
            self.in_battle = False
            return

        if self.turn_count == self.joke_active_turn:
            self.joke_effect = False
            self.joke_active_turn = None

        content = f"ターン{self.turn_count} - あなたのターン！現在のHP: {self.player_hp}\n選択肢: 攻撃, 行動, アイテム, 逃げる"
        view = SansBattleView(self.bot, self.ctx, self)

        if self.message is None:
            self.message = await self.ctx.followup.send(content, view=view)
        else:
            await self.message.edit(content=content, view=view)

    # 以下、handle_buttonやplayer_attackなども同様にVCと音声ファイルのパス固定で安全に呼ぶ
    # （省略していますが元のコードと同じ構造です）

class SansBattle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sans_battle", description="サンズとの戦闘を開始します。")
    async def sans_battle(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("先にVCに参加してください！", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc is None:
            vc = await channel.connect(timeout=30, reconnect=True)
        elif vc.channel != channel:
            await vc.move_to(channel)

        await interaction.response.defer(ephemeral=True)
        battle = SansBattleInstance(self.bot, interaction, vc)
        await battle.start()

async def setup(bot):
    await bot.add_cog(SansBattle(bot))
