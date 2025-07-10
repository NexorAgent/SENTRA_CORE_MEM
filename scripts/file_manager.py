import getpass
import os
import shutil
import time
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "actions.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _log(action: str, path: str, result: str) -> None:
    user = os.getenv("USER") or os.getenv("USERNAME") or getpass.getuser()
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    entry = f"{ts}\t{user}\t{action}\t{path}\t{result}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(entry)


def delete_file(path: str, validate_before_delete: bool = True) -> bool:
    target = Path(path)
    if validate_before_delete and not target.exists():
        _log("delete", str(target), "not_found")
        return False
    try:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink(missing_ok=True)
        _log("delete", str(target), "deleted")
        return True
    except Exception as e:
        _log("delete", str(target), f"error:{e}")
        raise


def move_file(src: str, dst: str) -> bool:
    s = Path(src)
    d = Path(dst)
    try:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        _log("move", f"{s}->{d}", "moved")
        return True
    except Exception as e:
        _log("move", f"{s}->{d}", f"error:{e}")
        raise


def archive_file(path: str, archive_dir: str) -> bool:
    src = Path(path)
    dst_dir = Path(archive_dir)
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        shutil.move(str(src), str(dst))
        _log("archive", f"{src}->{dst}", "archived")
        return True
    except Exception as e:
        _log("archive", f"{src}->{archive_dir}", f"error:{e}")
        raise
