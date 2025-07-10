import os
import subprocess
from pathlib import Path

def git_commit_push(files: list[Path], message: str) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    rel_files = [str(f.relative_to(repo_root)) for f in files if f.exists()]

    # --- Configuration git user (patch immédiat) ---
    subprocess.run(
        ["git", "config", "--global", "user.email", os.getenv("GIT_USER_EMAIL", "sentra-bot@localhost")],
        check=False, cwd=repo_root
    )
    subprocess.run(
        ["git", "config", "--global", "user.name", os.getenv("GIT_USER_NAME", "SentraCoreBot")],
        check=False, cwd=repo_root
    )

    # (reste de la fonction identique, avec le patch GitHub token déjà ajouté)
    github_username = os.getenv("GITHUB_USERNAME")
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo_url = os.getenv("GITHUB_REPO_URL")
    if github_username and github_token and github_repo_url:
        full_url = f"https://{github_username}:{github_token}@{github_repo_url}"
        try:
            subprocess.run(
                ["git", "remote", "set-url", "origin", full_url],
                check=True,
                cwd=repo_root,
            )
        except Exception as e:
            print(f"⚠️ Impossible de reconfigurer le remote git : {e}")

    try:
        subprocess.run(["git", "add", *rel_files], check=True, cwd=repo_root)
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=repo_root)
        subprocess.run(["git", "push"], check=True, cwd=repo_root)
        print("✅ Git commit/push réussi.")
    except subprocess.CalledProcessError as exc:
        print(f"⚠️ Git command failed: {exc}")
