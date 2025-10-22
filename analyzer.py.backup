# -*- coding: utf-8 -*-
import os
from datetime import datetime
from pathlib import Path

def load_api_key_safe() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    except Exception:
        api_key = None
    return api_key or ""

def _call_gpt(text: str, api_key: str) -> dict:
    if not api_key:
        lang = "de" if " der " in text or " und " in text else "en"
        return {
            "language": lang,
            "topic": "Unbestimmt",
            "keywords": [],
            "summary": "",
            "is_prompt": ("system prompt" in text.lower() or "systemprompt" in text.lower()),
            "is_llm_output": ("assistant" in text.lower() or "gpt" in text.lower()),
            "git_project": "",
            "confidence": 0.0,
        }
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        sys_prompt = (
            "Du bist ein präziser Metadaten-Extraktor. "
            "Gib eine JSON-Antwort mit den Feldern: language, topic, keywords (Liste), summary, "
            "is_prompt (bool), is_llm_output (bool), git_project (String), confidence (0..1). "
            "Antworte ausschließlich mit JSON, ohne Zusatztext."
        )
        user_prompt = f"Analysiere folgenden Text:\n\n{text[:20000]}"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()
        import json
        data = json.loads(content)
        data.setdefault("language", "")
        data.setdefault("topic", "")
        data.setdefault("keywords", [])
        data.setdefault("summary", "")
        data.setdefault("is_prompt", False)
        data.setdefault("is_llm_output", False)
        data.setdefault("git_project", "")
        data.setdefault("confidence", 0.0)
        return data
    except Exception:
        return {
            "language": "",
            "topic": "AnalyseFehler",
            "keywords": [],
            "summary": "",
            "is_prompt": False,
            "is_llm_output": False,
            "git_project": "",
            "confidence": 0.0,
        }

def embed_text(text: str, api_key: str):
    if not api_key:
        return []
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(
            model="text-embedding-3-large",
            input=text[:20000],
        )
        return resp.data[0].embedding
    except Exception:
        return []

def analyze_text(text: str, filename: str, filepath: str, source_extension: str, source_type: str, enable_embeddings: bool, api_key: str) -> dict:
    wordcount = len(text.split())
    created_at = ""
    try:
        p = Path(filepath)
        ts = p.stat().st_mtime
        from datetime import datetime
        created_at = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    except Exception:
        created_at = ""

    info = _call_gpt(text, api_key=api_key)
    embedding = embed_text(text, api_key=api_key) if enable_embeddings else []

    return {
        "filename": filename,
        "filepath": filepath,
        "source_extension": source_extension,
        "source_type": source_type,
        "language": info.get("language", ""),
        "topic": info.get("topic", ""),
        "keywords": info.get("keywords", []),
        "summary": info.get("summary", ""),
        "is_prompt": bool(info.get("is_prompt", False)),
        "is_llm_output": bool(info.get("is_llm_output", False)),
        "git_project": info.get("git_project", ""),
        "created_at": created_at,
        "wordcount": wordcount,
        "confidence": float(info.get("confidence", 0.0)),
        "embedding": embedding,
    }
