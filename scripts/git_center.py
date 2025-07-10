import subprocess


def run(cmd, cwd=None, capture=True):
    print(f"\n> {cmd}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, shell=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result


def menu():
    print(
        """
┌──────────────────────────────────────────────┐
│                  GIT CENTER                  │
├───── Actions possibles : ─────────────────────┤
│ 1. git status      2. git pull               │
│ 3. git push        4. git add .              │
│ 5. git commit      6. git clone              │
│ 7. git checkout    8. git branch             │
│ 9. git merge      10. git fetch              │
│11. git log        12. git reset              │
│13. git remote     14. git diff               │
│15. git rm         16. git stash              │
│17. git config     18. Quitter                │
└──────────────────────────────────────────────┘
"""
    )


def main():
    repo = input("Chemin du repo git (ou vide pour dossier actuel) : ").strip() or "."
    while True:
        menu()
        choix = input("Numéro de l'action : ").strip()
        if choix == "1":
            run("git status", cwd=repo)
        elif choix == "2":
            run("git pull", cwd=repo)
        elif choix == "3":
            run("git push", cwd=repo)
        elif choix == "4":
            run("git add .", cwd=repo)
        elif choix == "5":
            msg = input("Message de commit : ")
            run(f'git commit -m "{msg}"', cwd=repo)
        elif choix == "6":
            url = input("URL du dépôt à cloner : ")
            dossier = input("Dossier cible (ou vide) : ").strip()
            cmd = f"git clone {url}" + (f" {dossier}" if dossier else "")
            run(cmd)
        elif choix == "7":
            branche = input("Branche à checkout (ex: main/dev/feature...) : ")
            run(f"git checkout {branche}", cwd=repo)
        elif choix == "8":
            run("git branch -a", cwd=repo)
        elif choix == "9":
            branche = input("Branche à fusionner (merge dans la courante): ")
            run(f"git merge {branche}", cwd=repo)
        elif choix == "10":
            run("git fetch", cwd=repo)
        elif choix == "11":
            run("git log --oneline --graph --all -n 20", cwd=repo)
        elif choix == "12":
            mode = input("Mode reset [--soft/--mixed/--hard] : ").strip() or "--hard"
            cible = input("Commit (hash court ou HEAD~1 etc): ").strip()
            run(f"git reset {mode} {cible}", cwd=repo)
        elif choix == "13":
            run("git remote -v", cwd=repo)
        elif choix == "14":
            run("git diff", cwd=repo)
        elif choix == "15":
            fichier = input("Fichier à supprimer (ex: test.py): ")
            run(f"git rm {fichier}", cwd=repo)
        elif choix == "16":
            op = input("[push/pop/list/clear]: ").strip()
            if op == "push":
                run("git stash push", cwd=repo)
            elif op == "pop":
                run("git stash pop", cwd=repo)
            elif op == "list":
                run("git stash list", cwd=repo)
            elif op == "clear":
                run("git stash clear", cwd=repo)
        elif choix == "17":
            param = input("Paramètre à config (ex: user.name) : ")
            value = input("Valeur : ")
            run(f'git config {param} "{value}"', cwd=repo)
        elif choix == "18":
            print("Bye 👋")
            break
        else:
            print("Choix inconnu.")


if __name__ == "__main__":
    main()
