# -*- coding: utf-8 -*-
import re
from pathlib import Path

def ensure_processed_dir(source_dir: Path) -> Path:
    d = source_dir / "_processed"
    d.mkdir(exist_ok=True, parents=True)
    return d

def log_error(log_path: Path, message: str):
    log_path.parent.mkdir(exist_ok=True, parents=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def safe_relpath(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

def slugify_filename(name: str) -> str:
    name = re.sub(r"[^\w\-.]+", "_", name, flags=re.UNICODE)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "document"
