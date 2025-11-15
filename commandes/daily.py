from discord.ext import commands
import discord
import orjson
import os
import time  # pour gérer le cooldown

DATA_PATH = "données/coins-data.json"
DAILY_REWARD = 50000        # récompense quotidienne
COOLDOWN = 24 * 60 * 60    # 24 heures en secondes


def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "rb") as f:
        return orjson.loads(f.read())


def save_data(data):
    with open(DATA_PATH, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="daily")
    async def daily(self, ctx):
        user = ctx.author
        user_id = str(user.id)

        data = load_data()

        # ----- Création auto du profil -----
        if user_id not in data:
            data[user_id] = {
                "wallet": 100,
                "bank": 0,
                "diamonds": 0,
                "daily_timestamp": 0
            }

        # ----- Vérification cooldown -----
        now = time.time()
        last = data[user_id].get("daily_timestamp", 0)

        remaining = (last + COOLDOWN) - now

        if remaining > 0:
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)

            return await ctx.reply(
                f"⏳ Tu as déjà récupéré ton daily.\n"
                f"Reviens dans **{hours}h {minutes}m {seconds}s**."
            )

        # ----- Donner la récompense -----
        data[user_id]["wallet"] += DAILY_REWARD
        data[user_id]["daily_timestamp"] = now

        save_data(data)

        # ----- Embed -----
        embed = discord.Embed(
            title="🎁 Récompense quotidienne",
            description=f"{user.mention} a récupéré **{DAILY_REWARD} coins** !",
            color=discord.Color.blue()
        )

        embed.add_field(name="🪙 Nouveau wallet", value=f"**{data[user_id]['wallet']}**", inline=False)
        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text="Revient demain pour plus de rewards !")

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Daily(bot))
