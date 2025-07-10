# agent_squery.py
import subprocess


def run(intent=None, agent=None, date=None, tag=None, export=None):
    """
    Appelle le module SQUERY.py avec les paramètres fournis.
    """
    print("[SQUERY AGENT] Démarrage de la requête mémoire glyphée...")

    command = ["python", "./scripts/SQUERY.py"]

    if intent:
        command += ["--intent", intent]
    if agent:
        command += ["--agent", agent]
    if date:
        command += ["--date", date]
    if tag:
        command += ["--tag", tag]
    if export:
        command += ["--export", export]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Erreur dans SQUERY:", result.stderr)
        return f"Erreur : {result.stderr}"

    print("✅ Résultat SQUERY :\n", result.stdout)
    return result.stdout
