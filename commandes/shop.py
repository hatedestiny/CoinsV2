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

def save_data(data):
    with open(DATA_PATH, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


ITEMS = {
    "anti-rob": {
        "price": 1500,
        "duration": 3600,  # 1h
        "desc": "Empêche qu’on te vole pendant 1 heure."
    },
    "anti-crime": 
    {
        "price": 2000,
        "duration": 3600,
        "desc": "Empêche d’échouer un crime pendant 1 heure."
    }
}


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop")
    async def shop(self, ctx):
        embed = discord.Embed(
            title="🛒 Shop CoinsV2",
            color=discord.Color.gold()
        )

        for name, item in ITEMS.items():
            embed.add_field(
                name=f"**{name}** — {item['price']} coins",
                value=item["desc"],
                inline=False
            )

        await ctx.reply(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, item_name=None):
        if item_name is None:
            return await ctx.reply("❌ Utilise : `!buy item`")

        item_name = item_name.lower()

        if item_name not in ITEMS:
            return await ctx.reply("❌ Cet item n’existe pas dans le shop.")

        user_id = str(ctx.author.id)
        data = load_data()

        # Création auto
        if user_id not in data:
            data[user_id] = {
                "wallet": 100,
                "bank": 0,
                "diamonds": 0,
                "work_streak": 0,
                "last_work": 0,
                "work_timestamp": 0,
                "total_robbed": 0,
                "crime_success": 0,
                "crime_fail": 0,
                "items": {
                    "anti_rob_until": 0,
                    "anti_crime_until": 0
                }
            }

        user = data[user_id]

        # Prix + durée
        item = ITEMS[item_name]
        price = item["price"]
        duration = item["duration"]

        if user["wallet"] < price:
            return await ctx.reply("❌ Tu n’as pas assez de coins.")

        # Paiement
        user["wallet"] -= price

        now = int(time.time())

        if item_name == "anti-rob":
            user["items"]["anti_rob_until"] = now + duration

        elif item_name == "anti-crime":
            user["items"]["anti_crime_until"] = now + duration

        save_data(data)

        await ctx.reply(
            f"✅ Tu as acheté **{item_name}** pour **{price} coins** !"
        )


async def setup(bot):
    await bot.add_cog(Shop(bot))
