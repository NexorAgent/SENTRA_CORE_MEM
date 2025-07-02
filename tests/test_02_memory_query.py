import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.compose_prompt import load_memory_and_ask

# Tester la relecture d’une mémoire compressée avec une question
try:
    project = "test_project"
    question = "Quels sont les événements prévus dans le projet SENTRA HALLE ?"

    result = load_memory_and_ask(project, question)
    print("✅ Test lecture mémoire via GPT réussi.")
    print(result)

except Exception as e:
    print("❌ Échec de la lecture mémoire via GPT.")
    print(str(e))

