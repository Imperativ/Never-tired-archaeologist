# Archaeologist v2 — Semantische Dokument-Analyse mit Duplikaterkennung (GUI, lokal)

**Neu:** Duplikaterkennung über Embeddings (Cosine-Similarity).

## Features
- Tkinter-GUI (Deutsch): Ordner wählen, „Scannen & Exportieren“, optional Embeddings
- Rekursiver Scan: `.txt`, `.md`, `.pdf`, `.py`, `.json`, `.csv`, `.html`
- GPT-Metadaten + optional Embeddings
- **Duplikate** werden erkannt und im YAML markiert: `duplicate_of`, `similarity_score`
- Export pro Datei als Markdown (`_processed/<name>.md`) mit YAML-Header + Originaltext
- Fehler werden übersprungen und in `_processed/error_log.txt` protokolliert

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Trage deinen OpenAI API Key in .env ein
```

## Start
```bash
python main.py
```

## Hinweise
- Für die Duplikaterkennung aktiviere die Checkbox **Embeddings** im GUI (Standard: an).
- Schwellwert ist in `main.py` als `SIM_THRESHOLD = 0.95` gesetzt.
- PDFs benötigen `PyMuPDF`.

## Sicherheit
- API-Key bleibt lokal in `.env` oder Umgebungsvariable `OPENAI_API_KEY`.
