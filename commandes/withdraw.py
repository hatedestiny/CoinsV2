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


class Withdraw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="withdraw", aliases=["wd"])
    async def withdraw(self, ctx, amount=None):
        user = ctx.author
        user_id = str(user.id)

        data = load_data()

        # Création auto du profil
        if user_id not in data:
            data[user_id] = {
                "wallet": 100,
                "bank": 0,
                "diamonds": 0
            }
            save_data(data)

        wallet = data[user_id]["wallet"]
        bank = data[user_id]["bank"]

        # ---------------- Paramètre manquant ----------------
        if amount is None:
            return await ctx.reply("❌ Merci d’indiquer un montant : `!withdraw 500` ou `!withdraw all`")

        # ---------------- Gestion du "all" ----------------
        if isinstance(amount, str) and amount.lower() == "all":
            if bank <= 0:
                return await ctx.reply("❌ Ta banque est vide, tu ne peux rien retirer.")
            amount = bank  # On retire tout

        else:
            # Vérifier si c'est un nombre
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.reply("❌ Montant invalide. Utilise un nombre ou `all`.")

            if amount <= 0:
                return await ctx.reply("❌ Le montant doit être positif.")

            if amount > bank:
                return await ctx.reply(f"❌ Tu n'as pas assez d’argent dans ta banque ! (Tu as {bank})")

        # ---------------- Retrait ----------------
        data[user_id]["bank"] -= amount
        data[user_id]["wallet"] += amount

        save_data(data)

        # ---------------- Embed ----------------
        embed = discord.Embed(
            title="💼 Retrait effectué",
            description=f"{user.mention} a retiré **{amount} coins** de sa banque.",
            color=discord.Color.green()
        )

        embed.add_field(name="🏦 Nouvelle banque", value=f"**{data[user_id]['bank']}**", inline=False)
        embed.add_field(name="🪙 Nouveau wallet", value=f"**{data[user_id]['wallet']}**", inline=False)

        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text="Système d'économie CoinsV2")

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Withdraw(bot))
