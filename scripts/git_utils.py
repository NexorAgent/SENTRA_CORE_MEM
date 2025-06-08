import subprocess
from typing import Iterable

__all__ = ["commit_changes"]


def commit_changes(files: Iterable[str], message: str) -> None:
    """Add, commit and push specified files to git.

    Parameters
    ----------
    files : Iterable[str]
        Paths to files to add and commit.
    message : str
        Commit message.

    Raises
    ------
    RuntimeError
        If any git command fails.
    """
    paths = list(files)
    try:
        subprocess.run(["git", "add", *paths], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {e}")
