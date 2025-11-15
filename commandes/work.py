from discord.ext import commands
import random
import orjson
import os
import time

DATA_PATH = "données/coins-data.json"


def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "rb") as f:
        return orjson.loads(f.read())


def save_data(data):
    with open(DATA_PATH, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        user_id = str(ctx.author.id)
        now = int(time.time())

        data = load_data()

        # ----- Création auto du profil -----
        if user_id not in data:
            data[user_id] = {
                "wallet": 100,
                "bank": 0,
                "diamonds": 0,

                # Streak et timestamp
                "work_streak": 0,
                "last_work": 0,
                "work_timestamp": 0  # <--- AJOUT ICI
            }

        user = data[user_id]

        # ----- Gestion du streak -----
        last = user["last_work"]

        if last == 0:
            user["work_streak"] = 1
        else:
            if now - last <= 86400:  # moins de 24h
                user["work_streak"] += 1
            else:
                user["work_streak"] = 1

        streak = user["work_streak"]

        # ----- Gain -----
        gain_base = random.randint(500, 5000)
        bonus = streak * 100
        gain_total = gain_base + bonus

        user["wallet"] += gain_total

        # ----- Mise à jour timestamps -----
        user["last_work"] = now
        user["work_timestamp"] = now  # <--- Sauvegardé dans coins-data.json

        save_data(data)

        await ctx.send(
            f"💼 Tu as travaillé et tu as gagné **{gain_total} coins** !\n"
            f"🔥 **Streak : {streak}** (+{bonus} bonus)"
        )

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)

            return await ctx.reply(
                f"⏳ Tu dois attendre **{minutes}m {seconds}s** avant de retravailler !"
            )


async def setup(bot):
    await bot.add_cog(Work(bot))
