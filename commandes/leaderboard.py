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


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx, category: str = "total"):

        category = category.lower()
        valid_categories = ["wallet", "bank", "diamonds", "voleurs", "total"]

        if category not in valid_categories:
            return await ctx.reply(
                "❌ Catégorie invalide ! Choisis parmi : `wallet`, `bank`, `diamonds`, `voleurs`, `total`"
            )

        data = load_data()

        # Ajout automatique du champ total_robbed si manquant
        for uid in data:
            if "total_robbed" not in data[uid]:
                data[uid]["total_robbed"] = 0

        save_data(data)

        # ---------- Définition des valeurs selon la catégorie ----------
        def get_value(userdata):
            if category == "wallet":
                return userdata["wallet"]
            elif category == "bank":
                return userdata["bank"]
            elif category == "diamonds":
                return userdata["diamonds"]
            elif category == "voleurs":
                return userdata["total_robbed"]
            elif category == "total":
                return userdata["wallet"] + userdata["bank"]

        # ---------- Tri du leaderboard ----------
        sorted_users = sorted(
            data.items(),
            key=lambda item: get_value(item[1]),
            reverse=True
        )

        # Limite à 10 meilleurs
        top10 = sorted_users[:10]

        # ---------- Construction de l'affichage ----------
        lb_text = ""
        rank = 1

        for user_id, userdata in top10:
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"Utilisateur {user_id}"

            value = get_value(userdata)
            lb_text += f"**#{rank}** — **{name}** : `{value}`\n"
            rank += 1

        # ---------- Embed ----------
        title_map = {
            "wallet": "Top Wallet 💰",
            "bank": "Top Banque 🏦",
            "diamonds": "Top Diamants 💎",
            "voleurs": "Top Voleurs 🦹",
            "total": "Top Richesse Totale 💸"
        }

        embed = discord.Embed(
            title=title_map[category],
            description=lb_text if lb_text else "Personne n’a encore de données.",
            color=discord.Color.gold()
        )

        embed.set_footer(text="Système d'économie CoinsV2")

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
