import os
import subprocess
from datetime import datetime
from scripts.corrector.agent_openrouter import correct_with_openrouter

def run_ruff_fix(file_path):
    try:
        result = subprocess.run(
            ["ruff", "check", "--fix", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "✅ Ruff a corrigé le fichier."
        else:
            return False, f"⚠️ Ruff a renvoyé un code {result.returncode} :\n{result.stderr}"
    except Exception as e:
        return False, f"❌ Erreur Ruff : {str(e)}"

def test_python_execution(file_path):
    try:
        exec(open(file_path).read(), {})
        return True, "✅ Test d'exécution : OK"
    except Exception as e:
        return False, f"❌ Erreur d’exécution : {str(e)}"

def generate_report(file_path, ruff_result, gemini_result, test_result):
    report = f"# Rapport de correction – {datetime.now().isoformat()}\n"
    report += f"## Fichier : `{file_path}`\n\n"

    report += "### Ruff\n"
    report += f"{ruff_result[1]}\n\n"

    report += "### OpenRouter\n"
    report += f"{gemini_result[1]}\n\n"

    report += "### Test d’exécution\n"
    report += f"{test_result[1]}\n"

    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/correction_{os.path.basename(file_path)}.md"
    with open(log_path, "w") as f:
        f.write(report)
    return log_path

def main(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        return

    print(f"📂 Fichier à traiter : {file_path}\n")

    ruff_result = run_ruff_fix(file_path)
    print(ruff_result[1])

    gemini_result = correct_with_openrouter(file_path)
    print(f"🧠 Résultat OpenRouter : {gemini_result[1]}")

    test_result = test_python_execution(file_path)
    print(test_result[1])

    rapport_path = generate_report(file_path, ruff_result, gemini_result, test_result)
    print(f"\n📄 Rapport généré : {rapport_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage : python sentra_corrector_agent.py chemin/fichier.py")
    else:
        main(sys.argv[1])
