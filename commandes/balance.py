from discord.ext import commands
import discord
import orjson
import os

DATA_PATH = "données/coins-data.json"


def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "rb") as f:
        return orjson.loads(f.read())


def save_data(data):
    with open(DATA_PATH, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx):
        user = ctx.author
        user_id = str(user.id)

        data = load_data()

        # Si le joueur n'existe pas -> on le crée
        if user_id not in data:
            data[user_id] = {
                "wallet": 100,
                "bank": 0,
                "diamonds": 0
            }
            save_data(data)

        wallet = data[user_id]["wallet"]
        bank = data[user_id]["bank"]
        diamonds = data[user_id]["diamonds"]

        # ----- EMBED -----
        embed = discord.Embed(
            title=f"{user.display_name}", 
            description="Voici tes richesses 💰",
            color=discord.Color.gold()
        )

        embed.add_field(name="🪙 Coins dans le wallet", value=f"**{wallet}**", inline=False)
        embed.add_field(name="🏦 Banque", value=f"**{bank}**", inline=False)
        embed.add_field(name="💎 Diamants", value=f"**{diamonds}**", inline=False)

        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text="Système d'économie CoinsV2")

        # Envoyer en réponse à l'auteur
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Balance(bot))
