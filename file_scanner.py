# -*- coding: utf-8 -*-
from pathlib import Path

SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".py", ".json", ".csv", ".html"}

def iter_supported_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file():
            yield p
