# -*- coding: utf-8 -*-
from pathlib import Path

def readable_extension(ext: str) -> bool:
    ext = (ext or "").lower()
    return ext in {".txt", ".md", ".pdf", ".py", ".json", ".csv", ".html"}

def infer_source_type(ext: str) -> str:
    ext = (ext or "").lower()
    mapping = {
        ".txt": "text",
        ".md": "markdown",
        ".pdf": "pdf",
        ".py": "python",
        ".json": "json",
        ".csv": "csv",
        ".html": "html",
    }
    return mapping.get(ext, "unknown")

def _read_text_fallback(p: Path) -> str:
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def extract_text(p: Path) -> str:
    ext = p.suffix.lower()
    if ext in {".txt", ".md", ".py", ".json", ".csv", ".html"}:
        return _read_text_fallback(p)

    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
        except Exception as e:
            raise RuntimeError("PyMuPDF (fitz) ist nicht installiert. Bitte 'pip install pymupdf' ausführen.") from e
        out = []
        with fitz.open(str(p)) as doc:
            for page in doc:
                out.append(page.get_text())
        return "\n".join(out)

    return ""
