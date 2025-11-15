from discord.ext import commands
import discord
import orjson
import os

CONFIG_PATH = "données/config.json"


def load_config():
    with open(CONFIG_PATH, "rb") as f:
        return orjson.loads(f.read())


class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()
        self.owner_id = int(self.config["Owner"])

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Commande pour faire quitter le serveur (OWNER ONLY)."""

        if ctx.author.id != self.owner_id:
            return await ctx.reply("❌ Seul **l’Owner du bot** peut utiliser cette commande.")

        guild = ctx.guild

        # Message avant de partir
        await ctx.reply(f"👋 Je quitte **{guild.name}** sur demande de l’Owner.")

        # Quitte le serveur
        await guild.leave()


async def setup(bot):
    await bot.add_cog(Leave(bot))
