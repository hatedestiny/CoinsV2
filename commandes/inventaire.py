from discord.ext import commands
import discord
import time
import orjson
import os

DATA_PATH = "données/coins-data.json"

def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "rb") as f:
        return orjson.loads(f.read())


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data()

        if user_id not in data:
            return await ctx.reply("❌ Tu n’as pas de profil. Fais `!work` d’abord.")

        user = data[user_id]
        items = user["items"]

        now = int(time.time())

        def remaining(ts):
            r = ts - now
            return f"{r//60}m {r%60}s" if r > 0 else "❌ Expiré"

        embed = discord.Embed(
            title=f"🎒 Inventaire de {ctx.author.display_name}",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🛡 Anti-Rob",
            value=f"Durée restante : **{remaining(items['anti_rob_until'])}**",
            inline=False
        )

        embed.add_field(
            name="🔫 Anti-Crime",
            value=f"Durée restante : **{remaining(items['anti_crime_until'])}**",
            inline=False
        )

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory(bot))
