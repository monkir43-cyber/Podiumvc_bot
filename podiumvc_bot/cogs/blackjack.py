import random
import discord
from discord import app_commands
from discord.ext import commands
from manager import player_data  # 関数が定義されている想定

CARD_VALUES = {
    "A": 11, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 10, "Q": 10, "K": 10
}
SUITS = ["♠", "♥", "♦", "♣"]

def draw_card():
    rank = random.choice(list(CARD_VALUES.keys()))
    suit = random.choice(SUITS)
    return f"{suit}{rank}"

def calculate_score(cards):
    total = 0
    aces = 0
    for card in cards:
        rank = card[1:]
        val = CARD_VALUES[rank]
        total += val
        if rank == "A":
            aces += 1
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

class Blackjack(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games = {}  # user_id: game data

    @app_commands.command(name="bj", description="ブラックジャックを開始します。コインをベットしてください。")
    @app_commands.describe(bet="ベットするコインの数")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        user_id = interaction.user.id

        if bet <= 0:
            await interaction.response.send_message("❌ ベットは1以上で指定してください。", ephemeral=True)
            return

        if player_data.get_coins(user_id) < bet:
            await interaction.response.send_message("❌ コインが足りません。", ephemeral=True)
            return

        if not player_data.remove_coins(user_id, bet):
            await interaction.response.send_message("❌ コインの更新に失敗しました。再度お試しください。", ephemeral=True)
            return

        player_cards = [draw_card(), draw_card()]
        dealer_cards = [draw_card(), draw_card()]
        self.games[user_id] = {
            "bet": bet,
            "player_cards": player_cards,
            "dealer_cards": dealer_cards,
            "stand": False
        }

        embed = discord.Embed(title="🃏 ブラックジャック 開始 🃏", color=discord.Color.gold())
        embed.add_field(name="あなたのカード", value=", ".join(player_cards), inline=False)
        embed.add_field(name="ディーラーの見えているカード", value=dealer_cards[0], inline=False)
        embed.set_footer(text=f"ベット: {bet} コイン")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hit", description="カードを引きます。")
    async def hit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.games:
            await interaction.response.send_message("❌ ブラックジャックを開始していません。/ブラックジャック でゲームを始めてください。", ephemeral=True)
            return

        game = self.games[user_id]
        if game["stand"]:
            await interaction.response.send_message("❌ すでにスタンドしています。/スタンド で結果を確認してください。", ephemeral=True)
            return

        new_card = draw_card()
        game["player_cards"].append(new_card)
        score = calculate_score(game["player_cards"])

        embed = discord.Embed(title="🃏 ヒット！", color=discord.Color.blue())
        embed.add_field(name="あなたのカード", value=", ".join(game["player_cards"]), inline=False)
        embed.add_field(name="合計", value=str(score), inline=False)

        if score > 21:
            embed.color = discord.Color.red()
            embed.add_field(name="結果", value="バースト！負けです。", inline=False)
            del self.games[user_id]
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stand", description="勝負に出ます。")
    async def stand(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.games:
            await interaction.response.send_message("❌ ブラックジャックを開始していません。/ブラックジャック でゲームを始めてください。", ephemeral=True)
            return

        game = self.games[user_id]
        if game["stand"]:
            await interaction.response.send_message("❌ すでにスタンドしています。", ephemeral=True)
            return

        game["stand"] = True
        player_score = calculate_score(game["player_cards"])
        dealer_cards = game["dealer_cards"]

        while calculate_score(dealer_cards) < 17:
            dealer_cards.append(draw_card())
        dealer_score = calculate_score(dealer_cards)

        embed = discord.Embed(title="🃏 スタンド 🃏", color=discord.Color.gold())
        embed.add_field(name="あなたのカード", value=", ".join(game["player_cards"]), inline=False)
        embed.add_field(name="あなたの合計", value=str(player_score), inline=False)
        embed.add_field(name="ディーラーのカード", value=", ".join(dealer_cards), inline=False)
        embed.add_field(name="ディーラーの合計", value=str(dealer_score), inline=False)

        bet = game["bet"]

        if dealer_score > 21 or player_score > dealer_score:
            embed.color = discord.Color.green()
            embed.add_field(name="結果", value=f"あなたの勝ち！ {bet * 2} コイン獲得！", inline=False)
            player_data.add_coins(user_id, bet * 2)
        elif player_score == dealer_score:
            embed.color = discord.Color.orange()
            embed.add_field(name="結果", value="引き分け。ベットを返却します。", inline=False)
            player_data.add_coins(user_id, bet)
        else:
            embed.color = discord.Color.red()
            embed.add_field(name="結果", value="負けました。コインは戻りません。", inline=False)

        del self.games[user_id]
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Blackjack(bot))
