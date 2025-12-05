# -*- coding: utf-8 -*-
from pathlib import Path

SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".py", ".json", ".csv", ".html"}

def iter_supported_files(root: Path):
    """
    Recursively yields only files with supported extensions.
    Skips hidden files and _processed directory.
    """
    for p in root.rglob("*"):
        if not p.is_file():
            continue

        # Skip hidden files and processed directory
        if p.name.startswith('.') or '_processed' in p.parts:
            continue

        # Check if extension is supported
        if p.suffix.lower() in SUPPORTED_EXTS:
            yield p
