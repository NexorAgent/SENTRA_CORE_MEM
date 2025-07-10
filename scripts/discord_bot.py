#!/usr/bin/env python3
"""
discord_bot.py — Bot Discord du projet SENTRA_CORE_MEM avec serveur Flask pour keep-alive
"""

import os
import sys
import threading
import traceback
from pathlib import Path

# ─── Chemin projet ───────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ─── Imports internes ────────────────────────────────────────
import discord
from discord.ext import commands
from flask import Flask

import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
from scripts.agent_markdown import run as run_markdown
from scripts.agent_notion import run as run_sync
from scripts.memory_agent import save_note_from_text
from sentra.dispatcher import detect_intent_and_route
from sentra.zarch import quick_query

# ─── Partie Flask ────────────────────────────────────────────
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "SENTRA_CORE_MEM bot is running ✅", 200


def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# ─── Partie Discord ──────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)


# ─── Slash commands ─────────────────────────────────────────
@client.tree.command(name="sync", description="Synchronise la mémoire (→ Notion)")
async def slash_sync(inter: discord.Interaction):
    await inter.response.defer(thinking=True, ephemeral=False)
    try:
        run_sync()
        await inter.followup.send("✅ Synchronisation vers Notion effectuée.")
    except Exception as e:
        await inter.followup.send(f"❌ Échec de la synchronisation : {e}")
        print(traceback.format_exc())


@client.tree.command(name="report", description="Génère le rapport Markdown du jour")
async def slash_report(inter: discord.Interaction):
    await inter.response.defer(thinking=True, ephemeral=False)
    try:
        res = run_markdown()
        await inter.followup.send(res.get("réponse", "📄 Rapport généré."))
    except Exception as e:
        await inter.followup.send(f"❌ Erreur rapport : {e}")
        print(traceback.format_exc())


@client.tree.command(name="memoire", description="Recherche dans la mémoire locale")
@discord.app_commands.describe(terme="Mot ou expression à rechercher")
async def slash_memoire(inter: discord.Interaction, terme: str):
    await inter.response.defer(thinking=True, ephemeral=False)
    try:
        blocs = quick_query(terme, depth=2, limit=4)
        print("[DEBUG /memoire]", terme, "→", blocs)
        if blocs:
            await inter.followup.send("🧠 Résultats :\n\n" + "\n\n".join(blocs))
        else:
            await inter.followup.send("🔍 Rien trouvé.")
    except Exception as e:
        print(traceback.format_exc())
        err = str(e)
        await inter.followup.send(f"❌ Erreur : {err}")


# ─── Message libre : analyse d’intentions, prise de notes ────
@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return

    resp = detect_intent_and_route(msg.content)
    intent = resp.get("intent")
    reply = resp.get("réponse", "")

    if reply:
        await msg.channel.send(reply)

    if intent == "save_note":
        save_note_from_text(msg.content)


# ─── READY : sync des commandes ──────────────────────────────
@client.event
async def on_ready():
    await client.tree.sync()
    print(f"✅ Bot connecté : {client.user}  |  Slash commands synchronisées")


# ─── RUN : démarre Flask + Discord ─────────────────────────
if __name__ == "__main__":
    print("=== Lancement du bot Discord SENTRA avec Flask keep-alive ===")

    # Lancer Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Lancer le bot Discord
    client.run(DISCORD_TOKEN)
