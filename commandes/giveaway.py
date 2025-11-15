from discord.ext import commands
import discord
import asyncio
import orjson
import os
import time
import random

DATA_PATH = "données/coins-data.json"
CONFIG_PATH = "données/config.json"


def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "rb") as f:
        return orjson.loads(f.read())


def save_data(data):
    with open(DATA_PATH, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return orjson.loads(f.read())


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()
        self.owner_id = int(self.config["Owner"])
        self.active_giveaways = {}  # message_id: {"prize":..., "type":..., "entries":[...]}

    # -------------------------------
    # ➤ Commande Giveaway
    # -------------------------------
    @commands.command(name="giveaway")
    async def giveaway(self, ctx, duration: int = None, reward_type: str = None, amount: int = None):

        if ctx.author.id != self.owner_id:
            return await ctx.reply("❌ Seul **l'owner du bot** peut lancer un giveaway.")

        if duration is None or reward_type is None or amount is None:
            return await ctx.reply("❌ Utilisation : `!giveaway <durée en secondes> <coins/diamants> <montant>`")

        reward_type = reward_type.lower()

        if reward_type not in ("coins", "diamants"):
            return await ctx.reply("❌ Le type de récompense doit être `coins` ou `diamants`.")

        # ---------------------
        # Embed du giveaway
        # ---------------------
        embed = discord.Embed(
            title="🎉 Giveaway CoinsV2",
            color=discord.Color.gold()
        )
        embed.add_field(name="⏳ Durée :", value=f"{duration} secondes")
        embed.add_field(name="🎁 Récompense :", value=f"**{amount} {reward_type}**")
        embed.add_field(name="📌 Comment participer :", value="Clique sur 🎉 pour entrer !")
        embed.set_footer(text=f"Lancé par {ctx.author}")

        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")

        # Enregistrer giveaway
        self.active_giveaways[message.id] = {
            "prize": amount,
            "type": reward_type,
            "entries": []
        }

        # DM logs
        owner = self.bot.get_user(self.owner_id)
        if owner:
            await owner.send(
                f"📢 **Giveaway lancé !**\n"
                f"Serveur : {ctx.guild.name}\n"
                f"Récompense : {amount} {reward_type}\n"
                f"Durée : {duration}s\n"
                f"Message ID : {message.id}"
            )

        # Attendre la fin
        await asyncio.sleep(duration)

        # ---------------------
        # Récupérer les participations
        # ---------------------
        message = await ctx.channel.fetch_message(message.id)
        users = await message.reactions[0].users().flatten()
        users = [u for u in users if not u.bot]

        if not users:
            await ctx.send("❌ Personne n'a participé au giveaway...")
            return

        winner = random.choice(users)
        gw = self.active_giveaways.pop(message.id)

        # Ajouter récompense au JSON
        data = load_data()
        uid = str(winner.id)

        if uid not in data:
            data[uid] = {
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

        if gw["type"] == "coins":
            data[uid]["wallet"] += gw["prize"]
        else:
            data[uid]["diamonds"] += gw["prize"]

        save_data(data)

        # Annonce publique
        await ctx.send(
            f"🎉 **Giveaway terminé !**\n"
            f"Gagnant : {winner.mention}\n"
            f"Récompense : **{gw['prize']} {gw['type']}**"
        )

        # DM Log au owner
        if owner:
            await owner.send(
                f"🏁 **Giveaway terminé !**\n"
                f"Gagnant : {winner} ({winner.id})\n"
                f"Récompense : {gw['prize']} {gw['type']}"
            )

    # -------------------------------
    # ➤ Commande REROLL
    # -------------------------------
    @commands.command(name="reroll")
    async def reroll(self, ctx, message_id: int = None):

        if message_id is None:
            return await ctx.reply("Utilise : `!reroll <message_id>`")

        # Autorisations
        if (
            ctx.author.id != self.owner_id
            and not ctx.author.guild_permissions.manage_guild
        ):
            return await ctx.reply("❌ Tu n'as pas la permission de reroll ce giveaway.")

        try:
            message = await ctx.channel.fetch_message(message_id)
        except:
            return await ctx.reply("❌ Message introuvable.")

        # récupérer participants
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if not reaction:
            return await ctx.reply("❌ Pas de réactions 🎉 trouvées.")

        users = await reaction.users().flatten()
        users = [u for u in users if not u.bot]

        if not users:
            return await ctx.reply("❌ Personne n'a participé.")

        # Nouveau gagnant
        winner = random.choice(users)

        await ctx.send(f"🔁 Nouveau gagnant : {winner.mention} 🎉")

        # Log DM owner
        owner = self.bot.get_user(self.owner_id)
        if owner:
            await owner.send(
                f"🔁 **Reroll effectué** par {ctx.author}\n"
                f"Nouveau gagnant : {winner}"
            )


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
