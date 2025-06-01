#!/usr/bin/env python3
"""
discord_bot.py — Bot Discord du projet SENTRA_CORE_MEM
"""

import sys, traceback
from pathlib import Path
import discord
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..")))
from sentra.zarch import quick_query   # ← nouvelle import


# ─── Chemin projet ───────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ─── Imports internes ────────────────────────────────────────
from sentra.dispatcher import detect_intent_and_route
from scripts.memory_agent   import save_note_from_text
from scripts.agent_notion   import run as run_sync
from scripts.agent_markdown import run as run_markdown
from scripts.memory_lookup  import search_memory
from configs.discord_config import DISCORD_TOKEN

# ─── Client + Intents ────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True          # pour le chat libre
client  = discord.Client(intents=intents)

# ─── NOUVEAU : arbre de slash-commands ───────────────────────
tree = discord.app_commands.CommandTree(client)

@tree.command(name="sync", description="Synchronise la mémoire (→ Notion)")
async def slash_sync(inter: discord.Interaction):
    await inter.response.defer(thinking=True, ephemeral=False)
    try:
        run_sync()                      # ton agent Notion
        await inter.followup.send("✅ Synchronisation vers Notion effectuée.")
    except Exception as e:
        await inter.followup.send(f"❌ Échec de la synchronisation : {e}")
        print(traceback.format_exc())

@tree.command(name="report", description="Génère le rapport Markdown du jour")
async def slash_report(inter: discord.Interaction):
    await inter.response.defer(thinking=True, ephemeral=False)
    try:
        res = run_markdown()
        await inter.followup.send(res.get("réponse", "📄 Rapport généré."))
    except Exception as e:
        await inter.followup.send(f"❌ Erreur rapport : {e}")
        print(traceback.format_exc())

@tree.command(name="memoire", description="Recherche dans la mémoire locale")
@discord.app_commands.describe(terme="Mot ou expression à rechercher")
async def slash_memoire(inter: discord.Interaction, terme: str):
    await inter.response.defer(thinking=True, ephemeral=False)
    try:
        blocs = quick_query(terme, depth=2, limit=4)
        print("[DEBUG /memoire]", terme, "→", blocs)    # ← AJOUT
        if blocs:
            await inter.followup.send("🧠 Résultats :\n\n" + "\n\n".join(blocs))
        else:
            await inter.followup.send("🔍 Rien trouvé.")

    except Exception as e:
        import traceback, textwrap
        print(traceback.format_exc())
        err = textwrap.shorten(str(e), 200)
        await inter.followup.send(f"❌ Erreur : {err}")

# ─── Message libre : analyse d’intentions, prise de notes ────
@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return

    resp   = detect_intent_and_route(msg.content)
    intent = resp.get("intent")
    reply  = resp.get("réponse", "")

    # réponse basique
    if reply:
        await msg.channel.send(reply)

    # prise de note
    if intent == "save_note":
        save_note_from_text(msg.content)

# ─── READY : sync des commandes ──────────────────────────────
@client.event
async def on_ready():
    await tree.sync()           # envoie /sync /report /memoire
    print(f"✅ Bot connecté : {client.user}  |  Slash commands synchronisées")

# ─── RUN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Lancement du bot Discord SENTRA ===")
    client.run(DISCORD_TOKEN)
