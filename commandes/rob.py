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


class Rob(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rob")
    @commands.cooldown(1, 2700, commands.BucketType.user)  # 45 minutes cooldown
    async def rob(self, ctx, member: discord.Member = None):

        if member is None:
            return await ctx.reply("❌ Utilise : `!rob @utilisateur`")

        if member.id == ctx.author.id:
            return await ctx.reply("❌ Tu ne peux pas te voler toi-même 🤡")

        thief_id = str(ctx.author.id)
        target_id = str(member.id)

        data = load_data()

        # --- Création automatique des profils ---
        for uid in (thief_id, target_id):
            if uid not in data:
                data[uid] = {
                    "wallet": 100,
                    "bank": 0,
                    "diamonds": 0,
                    "work_streak": 0,
                    "last_work": 0,
                    "work_timestamp": 0,
                    "total_robbed": 0,
                    "items": {                      # ← AJOUT inventaire si manquant
                        "anti_rob_until": 0,
                        "anti_crime_until": 0
                    }
                }

            # Ajout du champ si manquant
            if "total_robbed" not in data[uid]:
                data[uid]["total_robbed"] = 0

            if "items" not in data[uid]:
                data[uid]["items"] = {
                    "anti_rob_until": 0,
                    "anti_crime_until": 0
                }

        thief = data[thief_id]
        target = data[target_id]

        now = int(time.time())

        # 🔥 ANTI-ROB — empêche le vol si actif
        if target["items"].get("anti_rob_until", 0) > now:
            remaining = target["items"]["anti_rob_until"] - now
            minutes = remaining // 60
            seconds = remaining % 60
            return await ctx.reply(
                f"🛡 **{member.display_name} est protégé contre les vols !**\n"
                f"⏳ Protection restante : **{minutes}m {seconds}s**"
            )

        # --- Vérifier si la cible est volable ---
        if target["wallet"] < 50:
            return await ctx.reply("❌ Cette personne est trop pauvre pour être volée... 💀")

        # --- Calcul du montant volé (35% à 100%) ---
        percent = random.uniform(0.35, 1.0)
        stolen = max(1, int(target["wallet"] * percent))

        # --- Appliquer le vol ---
        target["wallet"] -= stolen
        thief["wallet"] += stolen

        # --- Mise à jour du total volé ---
        thief["total_robbed"] += stolen

        save_data(data)

        # --- Embed résultat ---
        embed = discord.Embed(
            title="🦹 Vol réussi !",
            description=f"{ctx.author.mention} a volé {member.mention} !",
            color=discord.Color.red()
        )

        embed.add_field(name="💰 Montant volé :", value=f"**{stolen} coins**", inline=False)
        embed.add_field(name="🎯 Pourcentage :", value=f"{int(percent * 100)}%", inline=False)
        embed.add_field(name="🦹 Total volé par toi :", value=f"**{thief['total_robbed']} coins**", inline=False)

        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text="Système d'économie CoinsV2")

        await ctx.reply(embed=embed)

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)
            return await ctx.reply(
                f"⏳ Tu dois attendre **{minutes}m {seconds}s** avant de voler quelqu’un !"
            )


async def setup(bot):
    await bot.add_cog(Rob(bot))
