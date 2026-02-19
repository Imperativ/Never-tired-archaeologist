# Never-Tired-Archaeologist v2.0

Ein lokales Python-Tool zur **semantischen Dokumentenanalyse**.

## 🎯 Features

- **Lokale Embeddings**: CPU-optimiert mit `sentence-transformers` (all-MiniLM-L6-v2)
- **LLM-Analyse**: Metadaten-Extraktion via Anthropic Claude API
- **SQLite-Datenbank**: Persistente Speicherung von Dokumenten, Metadaten und Embeddings
- **Duplikatserkennung**: SHA256-basierte Content-Hash-Prüfung
- **Strukturierte Ausgabe**: Pydantic-Modelle für type-safe Datenverarbeitung

## 📋 Voraussetzungen

- **Python 3.13**
- **CPU-only** (keine GPU/CUDA erforderlich)
- **Anthropic API Key** ([hier registrieren](https://console.anthropic.com/))

## 🚀 Installation

### 1. Repository klonen

```bash
git clone https://github.com/Imperativ/Never-tired-archaeologist.git
cd Never-tired-archaeologist
```

### 2. Virtuelle Umgebung erstellen

```bash
python -m venv .venv
```

### 3. Virtuelle Umgebung aktivieren

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 4. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 5. API-Key konfigurieren

Erstelle eine `.env` Datei im Projektverzeichnis:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## 📖 Verwendung

### Einzelnes Dokument analysieren

```bash
python main.py <pfad_zur_datei>
```

**Beispiel:**

```bash
python main.py test_document.txt
```

### Dokument erneut verarbeiten (trotz Duplikat)

```bash
python main.py <pfad_zur_datei> --force
```

## 📊 Extrahierte Metadaten

Das Tool extrahiert folgende Informationen:

- **Title**: Haupttitel oder Thema des Dokuments
- **Language**: ISO 639-1 Sprachcode (z.B. `de`, `en`)
- **Topics**: Liste der Hauptthemen
- **Summary**: Prägnante Zusammenfassung (2-3 Sätze)
- **Keywords**: Wichtige Schlüsselbegriffe

## 🗂️ Projektstruktur

```
Never-tired-archaeologist/
├── src/
│   ├── __init__.py          # Modul-Exporte
│   ├── models.py            # Pydantic-Datenmodelle
│   ├── database.py          # SQLite-Verwaltung
│   ├── embedder.py          # Lokale Embedding-Generierung
│   └── llm.py               # Claude API Integration
├── main.py                  # Haupt-Pipeline
├── requirements.txt         # Python-Dependencies
├── .env                     # API-Keys (nicht in Git!)
├── archaeologist.db         # SQLite-Datenbank (erstellt automatisch)
└── README.md
```

## 🔧 Konfiguration

### Claude-Modell ändern

In `src/llm.py` kannst du das Modell anpassen:

```python
analyzer = Analyzer(model="claude-3-5-sonnet-20241022")
```

Verfügbare Modelle:

- `claude-3-5-sonnet-20241022` (Standard)
- `claude-3-7-sonnet-latest` (falls verfügbar)
- `claude-3-opus-latest`

### Embedding-Modell ändern

In `src/embedder.py`:

```python
embedder = LocalEmbedder(model_name="all-MiniLM-L6-v2")
```

Alternative CPU-freundliche Modelle:

- `paraphrase-MiniLM-L6-v2`
- `all-mpnet-base-v2` (größer, aber präziser)

## 📝 Logging

Logs werden gespeichert in:

- **Konsole**: INFO-Level und höher
- **Datei**: `archaeologist.log` (alle Levels)

## 🛠️ Entwicklung

### Tests ausführen

```bash
pytest tests/
```

### Code-Style prüfen

```bash
flake8 src/
mypy src/
```

## 📦 Datenbank-Schema

**Tabelle: documents**

| Feld           | Typ       | Beschreibung                         |
| -------------- | --------- | ------------------------------------ |
| id             | INTEGER   | Primary Key                          |
| content_hash   | TEXT      | SHA256-Hash (für Duplikatserkennung) |
| content        | TEXT      | Volltext des Dokuments               |
| metadata_json  | TEXT      | JSON-serialisierte Metadaten         |
| embedding_json | TEXT      | JSON-Array des Embedding-Vektors     |
| created_at     | TIMESTAMP | Erstellungszeitpunkt                 |

## ⚠️ Bekannte Einschränkungen

- **Textlänge**: Maximal 100.000 Zeichen pro Dokument (Claude-Limit)
- **Dateiformate**: Aktuell nur Plain-Text (`.txt`)
- **API-Kosten**: Claude API ist kostenpflichtig (siehe [Anthropic Pricing](https://www.anthropic.com/pricing))

## 🚧 Roadmap

- [ ] PDF-Support
- [ ] DOCX-Support
- [ ] Batch-Processing
- [ ] Semantische Suche über Embeddings
- [ ] Web-UI mit Flask/FastAPI
- [ ] Export-Funktionen (CSV, JSON)

## 📄 Lizenz

MIT License - siehe LICENSE-Datei

## 🤝 Beitragen

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue öffnen.

## 🔗 Links

- [Anthropic API Docs](https://docs.anthropic.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [Pydantic](https://docs.pydantic.dev/)

## 📧 Kontakt

Bei Fragen oder Problemen bitte ein GitHub Issue erstellen.

---

**Archiv**: Der alte Ansatz (v1.0) ist im Branch `archive/old-approach-v1` gesichert.
