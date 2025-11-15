from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["aide", "commands", "cmds"])
    async def help(self, ctx, command_name: str = None):
        """Système de help avancé"""

        # ----------- HELP SANS ARGUMENT : liste des commandes -----------
        if command_name is None:
            embed = discord.Embed(
                title="📘 Menu d’aide — CoinsV2",
                description="Voici la liste des commandes disponibles :",
                color=discord.Color.blurple()
            )

            embed.add_field(
                name="💼 Économie",
                value=(
                    "`wallet` — Voir ton porte-monnaie\n"
                    "`balance` — Voir ton argent + banque\n"
                    "`deposit` — Déposer de l’argent\n"
                    "`withdraw` — Retirer de l’argent\n"
                    "`work` — Travailler pour gagner des coins\n"
                    "`daily` — Récompense quotidienne\n"
                ),
                inline=False
            )

            embed.add_field(
                name="🦹 Crime",
                value=(
                    "`rob` — Voler un utilisateur\n"
                    "`crime` — Tenter un crime (risqué)\n"
                ),
                inline=False
            )

            embed.add_field(
                name="🛒 Shop & Inventaire",
                value=(
                    "`shop` — Ouvrir le magasin\n"
                    "`buy` — Acheter un item\n"
                    "`inventory` — Voir tes objets / protections\n"
                ),
                inline=False
            )

            embed.add_field(
                name="🏆 Classements",
                value=(
                    "`leaderboard` — Voir les meilleurs joueurs\n"
                    "`lb wallet/bank/total/diamonds/robbers` — Classement détaillé\n"
                ),
                inline=False
            )

            embed.add_field(
                name="🎉 Giveaway",
                value=(
                    "`giveaway` — Créer un giveaway (staff seulement)\n"
                    "`reroll` — Choisir un nouveau gagnant (staff / owner)\n"
                ),
                inline=False
            )

            embed.add_field(
                name="🛠️ Administration",
                value=(
                    "`leave` — Le bot quitte le serveur (Owner uniquement)\n"
                ),
                inline=False
            )

            embed.set_footer(text="Utilise !help <commande> pour plus de détails.")
            return await ctx.reply(embed=embed)

        # ----------- HELP DÉTAILLÉ D’UNE COMMANDE -----------
        command = self.bot.get_command(command_name.lower())

        if command is None:
            return await ctx.reply("❌ Cette commande n’existe pas.")

        embed = discord.Embed(
            title=f"📘 Aide : {command.name}",
            color=discord.Color.green()
        )

        # Description
        embed.add_field(
            name="📄 Description",
            value=command.help or "Aucune description fournie.",
            inline=False
        )

        # Usage
        usage = f"!{command.name} {command.signature}".strip()
        embed.add_field(name="⚙️ Utilisation", value=f"`{usage}`", inline=False)

        # Alias
        if command.aliases:
            embed.add_field(
                name="🔀 Alias",
                value=", ".join([f"`{a}`" for a in command.aliases]),
                inline=False
            )

        await ctx.reply(embed=embed)



async def setup(bot):
    await bot.add_cog(Help(bot))
