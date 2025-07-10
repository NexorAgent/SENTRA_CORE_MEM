import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.agent_notion import send_to_notion

print("🚀 Test 05 Notion : lancement")
try:
    print("✅ Import agent_notion OK")
    result = send_to_notion(
        name="Test Notion - Mémoire SENTRA",
        titre="Mémoire envoyée depuis le test 05.",
        categorie="mémoire",
        statut="À valider",
        validation="auto",
        utilisation="pro",
        url=""
    )
    print("✅ Note envoyée à Notion avec succès :", result)
except Exception as e:
    import traceback
    print("❌ Échec envoi Notion :")
    traceback.print_exc()
