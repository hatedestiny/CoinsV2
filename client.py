import discord
from discord.ext import commands
import os
import orjson

# ---------- CHARGEMENT CONFIG ----------
CONFIG_PATH = "données/config.json"

with open(CONFIG_PATH, "rb") as f:
    config = orjson.loads(f.read())

prefix = config["Prefix"]
token = config["Token"]

# ---------- BOT ----------
intents = discord.Intents.all()
CoinsV2 = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)
# ---------- CHARGEMENT AUTOMATIQUE DES COGS ----------
async def load_cogs():
    """
    Charge tous les fichiers .py dans le dossier 'commandes'
    """
    for filename in os.listdir("commandes"):
        if filename.endswith(".py"):
            module = filename[:-3]  # retirer .py
            await CoinsV2.load_extension(f"commandes.{module}")
            print(f"[COG] chargé : {module}")


@CoinsV2.event
async def setup_hook():
    print("[INFO] Chargement des commandes (cogs)...")
    await load_cogs()
    print("[INFO] Tous les cogs sont chargés !")


# ---------- LANCEMENT ----------
@CoinsV2.event
async def on_ready():
    print(f"{CoinsV2.user.display_name} is ready ! ")


CoinsV2.run(token)
