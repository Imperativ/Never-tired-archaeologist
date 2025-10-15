# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
from utils import slugify_filename

def _yaml_escape_scalar(value):
    if value is None:
        return ""
    s = str(value)
    if any(ch in s for ch in [":", "-", "{", "}", "[", "]", ",", "#", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`"]):
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s

def _yaml_list(values):
    if not values:
        return "[]"
    out = ["["]
    for i, v in enumerate(values):
        if isinstance(v, float):
            item = f"{v:.6f}"
        elif isinstance(v, (int,)):
            item = str(v)
        else:
            sval = str(v).replace('"', '\\"')
            item = f'"{sval}"'
        out.append(item)
        if i < len(values) - 1:
            out.append(", ")
    out.append("]")
    return "".join(out)

def write_markdown_with_metadata(base_dir: Path, original_path: Path, text: str, metadata: dict) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    stem = slugify_filename(original_path.stem)
    out_name = f"{stem}.md"
    out_path = base_dir / out_name

    lines = ["---"]
    for key in [
        "filename","filepath","source_extension","source_type","language","topic",
        "keywords","summary","is_prompt","is_llm_output","git_project","created_at",
        "wordcount","confidence","embedding","duplicate_of","similarity_score"
    ]:
        value = metadata.get(key, "")
        if isinstance(value, list):
            val = _yaml_list(value)
        elif isinstance(value, bool):
            val = "true" if value else "false"
        elif isinstance(value, float):
            val = f"{value:.6f}"
        else:
            val = _yaml_escape_scalar(value)
        lines.append(f"{key}: {val}")
    lines.append("---\n")
    lines.append("# Originaltext\n")
    lines.append(text if text.endswith("\n") else text + "\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
