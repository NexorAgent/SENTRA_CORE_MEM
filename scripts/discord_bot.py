#!/usr/bin/env python3
"""
discord_bot.py — Bot Discord du projet SENTRA_CORE_MEM
Permet de capturer les messages, détecter intent, et renvoyer la réponse.
"""

import sys
from pathlib import Path

# ─────────────────────────────────────────────────
# Ajouter la racine du projet au chemin Python (pour imports relatifs)
# ─────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import discord
from sentra.dispatcher import detect_intent_and_route
from scripts.memory_agent import save_note_from_text
from scripts.agent_notion import run as run_sync       # Fonction de synchronisation Notion
from scripts.agent_markdown import run as run_markdown # Fonction de génération Markdown
from scripts.memory_lookup import search_memory       # Import du module de recherche mémoire
from configs.discord_config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[GPT] Connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 1) Détecter l'intention via le dispatcher
    response = detect_intent_and_route(message.content)
    intent = response.get("intent")
    reply_text = response.get("réponse", "")

    # 2) Si c'est une synchronisation, appeler l'agent Notion
    if intent == "sync_notion":
        try:
            run_sync()
            reply_text = "✅ Synchronisation vers Notion effectuée."
        except Exception as e:
            reply_text = f"❌ Échec de la synchronisation : {e}"

    # 3) Si c'est un rapport Markdown, appeler l'agent Markdown
    elif intent == "markdown_gen":
        try:
            result = run_markdown()
            reply_text = result.get("réponse", "📄 Rapport généré.")
        except Exception as e:
            reply_text = f"❌ Erreur lors de la génération du rapport : {e}"

    # 4) Si c'est un chat/interrogation, on interroge la mémoire
    elif intent == "chat":
        matches = search_memory(message.content, max_results=5)
        if matches:
            extrait = "\n".join(matches)
            reply_text = f"🧠 Extraits de mémoire pertinents :\n{extrait}"
        else:
            reply_text = "🔍 Désolé, je n'ai rien trouvé dans ma mémoire sur ce sujet."

    # 5) Envoyer la réponse dans le canal Discord
    await message.channel.send(reply_text)

    # 6) Si c'est une note, on sauvegarde
    if intent == "save_note":
        save_note_from_text(message.content)

if __name__ == "__main__":
    print("=== Lancement du bot Discord SENTRA ===")
    client.run(DISCORD_TOKEN)
