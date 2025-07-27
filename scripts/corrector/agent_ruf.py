import subprocess
import os

def correct_with_ruf(file_path):
    if not os.path.exists(file_path):
        return False, f"❌ Fichier introuvable : {file_path}"

    try:
        ruff_proc = subprocess.run(["ruff", "--fix", file_path], capture_output=True, text=True)
        black_proc = subprocess.run(["black", file_path], capture_output=True, text=True)

        summary = "✅ Formatage terminé.\n"
        summary += "🧹 Ruff :\n" + ruff_proc.stdout + ruff_proc.stderr + "\n"
        summary += "🧼 Black :\n" + black_proc.stdout + black_proc.stderr
        return True, summary

    except Exception as e:
        return False, f"❌ Erreur Ruff/Black : {str(e)}"
