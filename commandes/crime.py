from discord.ext import commands
import discord
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


class Crime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="crime")
    @commands.cooldown(1, 900, commands.BucketType.user)  # 15 minutes cooldown
    async def crime(self, ctx, member: discord.Member = None):

        if member is None:
            return await ctx.reply("❌ Utilise : `!crime @utilisateur`")

        if member.id == ctx.author.id:
            return await ctx.reply("❌ Tu ne peux pas te crime toi-même 🤡")

        criminal_id = str(ctx.author.id)
        target_id = str(member.id)

        data = load_data()
        now = int(time.time())

        # ----- Création automatique des profils -----
        for uid in (criminal_id, target_id):
            if uid not in data:
                data[uid] = {
                    "wallet": 100,
                    "bank": 0,
                    "diamonds": 0,
                    "work_streak": 0,
                    "last_work": 0,
                    "work_timestamp": 0,
                    "total_robbed": 0,
                    "items": {
                        "anti_rob_until": 0,
                        "anti_crime_until": 0
                    }
                }

            # Ajout des champs si manquants
            if "items" not in data[uid]:
                data[uid]["items"] = {
                    "anti_rob_until": 0,
                    "anti_crime_until": 0
                }

            if "total_robbed" not in data[uid]:
                data[uid]["total_robbed"] = 0

        criminal = data[criminal_id]
        target = data[target_id]

        # ----- ANTI-CRIME -----
        if target["items"]["anti_crime_until"] > now:
            remaining = target["items"]["anti_crime_until"] - now
            minutes = remaining // 60
            seconds = remaining % 60
            return await ctx.reply(
                f"🛡 **{member.display_name} est protégé contre les crimes !**\n"
                f"⏳ Protection restante : **{minutes}m {seconds}s**"
            )

        # ----- Vérif si cible assez riche -----
        if target["wallet"] < 50:
            return await ctx.reply("💀 Cette personne est trop pauvre pour que tu la crimes...")

        # ----- Calcul gain/perte -----
        # 60% réussir, 40% rater
        success = random.random() <= 0.60

        if success:
            # Réussite → voler 20 à 80 % du wallet
            percent = random.uniform(0.20, 0.80)
            stolen = max(1, int(target["wallet"] * percent))

            target["wallet"] -= stolen
            criminal["wallet"] += stolen

            msg = (
                f"🔪 **Crime réussi !**\n"
                f"Tu as attaqué {member.mention} et tu as volé **{stolen} coins** "
                f"({int(percent * 100)}%)."
            )

        else:
            # Échec → perte de 5 à 20 % de SON wallet
            percent = random.uniform(0.05, 0.20)
            lost = max(1, int(criminal["wallet"] * percent))

            criminal["wallet"] -= lost

            msg = (
                f"🚨 **Crime raté !**\n"
                f"{member.mention} t'a mis une énorme claque 💥\n"
                f"Tu perds **{lost} coins** ({int(percent * 100)}%)."
            )

        save_data(data)

        await ctx.reply(msg)

    @crime.error
    async def crime_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)
            return await ctx.reply(
                f"⏳ Tu dois attendre **{minutes}m {seconds}s** avant de commettre un crime !"
            )


async def setup(bot):
    await bot.add_cog(Crime(bot))
