# Archaeologist v3.0 — Semantische Dokumentenanalyse mit Multi-Provider LLMs

Lokales Tool zur intelligenten Dokumentenanalyse mit KI-gestützter Metadatenextraktion, Embedding-Vektorisierung, Duplikaterkennung und Volltextsuche.

## 🚀 Features

### Core-Funktionalität

- **Tkinter-GUI** (Deutsch): Intuitive Benutzeroberfläche für alle Funktionen
- **Rekursiver Dateiscan**: Unterstützt `.txt`, `.md`, `.pdf`, `.py`, `.json`, `.csv`, `.html`
- **Multi-Provider LLM-Architektur**:
  - **Claude Haiku 4.5** (Anthropic): Schnelle, präzise Metadaten-Analyse
  - **Gemini Embedding-001** (Google): Hochwertige Vektorisierung
- **SQLite-Datenbank mit FTS5**: Persistente Speicherung & blitzschnelle Volltextsuche
- **Duplikaterkennung**: Cosine-Similarity über Embeddings (Schwellwert: 0.95)
- **Volltext-Suche**: FTS5-basierte Suche direkt in der GUI
- **Optional**: Markdown-Export mit YAML-Frontmatter

### Metadaten-Extraktion

Die KI analysiert automatisch:

- Sprache (ISO 639-1 Code)
- Thema/Topic
- Keywords (Liste)
- Zusammenfassung
- LLM-Erkennung (ist_prompt, ist_llm_output)
- Git-Projekt-Erkennung
- Konfidenz-Score

### Datenbank-Schema

```
documents         → Kerndokumente (Dateiname, Pfad, Text, Wortanzahl, etc.)
metadata          → Extrahierte Metadaten (Sprache, Topic, Keywords, etc.)
embeddings        → Vektorembeddings (768 Dimensionen, BLOB)
duplicates        → Duplikat-Beziehungen
documents_fts     → FTS5 Volltextindex
```

## 📦 Installation

### Voraussetzungen

- Python 3.12+
- API-Keys für:
  - **Anthropic** (Claude)
  - **Google AI** (Gemini)

### Setup

```bash
# Repository klonen
git clone https://github.com/Imperativ/Never-tired-archaeologist.git
cd Never-tired-archaeologist

# Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# API-Keys konfigurieren
cp .env.example .env
# Trage deine API-Keys in .env ein (siehe unten)
```

### API-Keys Konfiguration

Erstelle eine `.env` Datei im Projektverzeichnis:

```env
# Anthropic API Key (für Claude Haiku 4.5)
ANTHROPIC_API_KEY=sk-ant-...

# Google AI API Key (für Gemini Embeddings)
GOOGLE_API_KEY=AIza...
# Alternative:
# GEMINI_API_KEY=AIza...
```

**API-Keys erhalten:**

- **Anthropic**: https://console.anthropic.com/
- **Google AI**: https://aistudio.google.com/app/apikey

## 🎯 Verwendung

### GUI starten

```bash
python main.py
```

### Workflow

1. **Ordner auswählen**: Klicke auf "Ordner auswählen" und wähle deinen Dokumentenordner
2. **Optionen konfigurieren**:
   - ☑ **Embeddings erzeugen** (empfohlen für Duplikaterkennung)
   - ☐ **Markdown-Dateien exportieren** (optional, da Datenbank primär)
3. **Scannen**: Klicke auf "Scannen & Analysieren"
4. **Suchen**: Nutze das Suchfeld für Volltextsuche in der Datenbank
5. **Statistiken**: Zeige Datenbank-Statistiken an

### Suche

Die Volltextsuche unterstützt FTS5-Syntax:

```
# Einfache Suche
Python

# Boolean-Operatoren
Python AND tutorial

# Phrase-Suche
"machine learning"

# Ausschluss
Python NOT tutorial

# Kombiniert
(Python OR JavaScript) AND tutorial
```

### Datenbank-Speicherort

Die Datenbank wird automatisch im gewählten Quellordner erstellt:

```
/dein/ordner/
├── archaeologist.db   ← Hier!
├── dokument1.pdf
├── dokument2.txt
└── ...
```

## 📊 GUI-Übersicht

```
┌───────────────────────────────────────────────────────────┐
│ Archaeologist — Dokument-Analysator v3.0.0               │
├───────────────────────────────────────────────────────────┤
│ Quellordner: /pfad/zu/deinen/dokumenten                  │
│ [Ordner auswählen...]                                     │
│                                                           │
│ ☑ Embeddings erzeugen (empfohlen für Duplikaterkennung) │
│ ☐ Zusätzlich Markdown-Dateien exportieren (optional)    │
│                                                           │
│ Suche in Datenbank:                                      │
│ [Suchbegriff eingeben...........................] [🔍]   │
│                                                           │
│ [Scannen & Analysieren] [Statistiken] [Log leeren]      │
│                                                           │
│ Status: Bereit.                                          │
│                                                           │
│ Protokoll:                                               │
│ ┌───────────────────────────────────────────────────────┐│
│ │[12:34:56] Verarbeite: dokument.pdf                   ││
│ │[12:34:57]   → Analysiere mit Claude Haiku 4.5...     ││
│ │[12:34:58]   → Sprache: de, Topic: Finanzen           ││
│ │[12:34:58]   ✓ In Datenbank gespeichert (ID: 42)     ││
│ │                                                       ││
│ └───────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────┘
```

## 🧪 Tests

Umfangreiche Test-Suite mit 214 Tests:

```bash
# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=. --cov-report=html

# Nur spezifische Module
pytest tests/test_database.py -v
pytest tests/test_main.py -v
```

**Test-Coverage:**

- `database.py` - SQLite-Operationen, FTS5-Suche
- `dupdetect.py` - Cosine-Similarity, Duplikaterkennung
- `file_scanner.py` - Rekursiver Scan, Filterung
- `text_extractor.py` - Text-Extraktion (7 Formate)
- `exporter.py` - Markdown-Export, YAML-Escaping
- `llm_providers.py` - Multi-Provider-Architektur
- `main.py` - GUI-Suchfunktionalität
- `utils.py` - Hilfsfunktionen

## 🏗️ Architektur

### Multi-Provider System

```python
MultiProvider
├── ClaudeProvider (Analyse)
│   └── Claude Haiku 4.5 (schnell, kostengünstig)
└── GeminiProvider (Embeddings)
    └── gemini-embedding-001 (768 Dimensionen)
```

**Vorteile:**

- **Austauschbar**: Provider können einfach gewechselt werden
- **Skalierbar**: Neue Provider über Abstract Base Classes hinzufügen
- **Fallback-fähig**: Bei Rate-Limits automatisch weitermachen

### Datenfluss

```
1. File Scanner  →  Dateien finden
2. Text Extractor  →  Text extrahieren
3. Claude Provider  →  Metadaten analysieren
4. Gemini Provider  →  Embedding generieren
5. Duplicate Detector  →  Duplikate finden
6. Database  →  Persistent speichern
7. (Optional) Exporter  →  Markdown exportieren
```

## 🔒 Sicherheit

- **Lokale Verarbeitung**: Alle Daten bleiben auf deinem System
- **API-Keys**: Werden niemals im Code gespeichert, nur in `.env`
- **Keine Cloud-Speicherung**: Datenbank ist lokal (SQLite)
- **.env in .gitignore**: Keys werden nicht versioniert

## 📝 Duplikaterkennung

Dokumente werden als Duplikate erkannt, wenn:

- Embeddings vorhanden sind
- Cosine-Similarity ≥ 0.95 (anpassbar in `main.py`: `SIM_THRESHOLD`)

**Duplikat-Markierung:**

```sql
SELECT d1.filename, d2.filename, dup.similarity_score
FROM duplicates dup
JOIN documents d1 ON dup.document_id = d1.id
JOIN documents d2 ON dup.duplicate_of_id = d2.id;
```

## 🛠️ Entwicklung

### Projekt-Struktur

```
Never-tired-archaeologist/
├── main.py                 # GUI & Hauptlogik
├── database.py             # SQLite + FTS5
├── llm_providers.py        # Multi-Provider-Architektur
├── text_extractor.py       # Text-Extraktion
├── file_scanner.py         # Rekursiver Scan
├── dupdetect.py            # Duplikaterkennung
├── exporter.py             # Markdown-Export
├── utils.py                # Hilfsfunktionen
├── requirements.txt        # Dependencies
├── .env.example            # API-Key-Vorlage
├── pytest.ini              # Test-Konfiguration
└── tests/                  # 214 Unit-Tests
    ├── test_database.py
    ├── test_llm_providers.py
    ├── test_main.py
    └── ...
```

### Dependencies

```
anthropic>=0.40.0          # Claude API
google-generativeai>=0.8.3 # Gemini API
PyMuPDF>=1.24.0            # PDF-Extraktion
pytest>=8.0.0              # Testing
pytest-cov>=5.0.0          # Coverage
python-dotenv>=1.0.0       # .env Support
```

## 🚨 Fehlerbehandlung

- **Rate-Limits**: Werden übersprungen, Log-Warnung
- **Fehlende API-Keys**: Warnung beim Start
- **Korrupte Dateien**: Fehler werden protokolliert in `error_log.txt`
- **Encoding-Probleme**: Automatischer Fallback auf alternative Encodings

## 📈 Statistiken

Zeige Datenbank-Statistiken über den "Statistiken"-Button:

- Anzahl Dokumente
- Anzahl Embeddings
- Anzahl Duplikate
- Verteilung nach Sprachen
- Verteilung nach Dateitypen

## 🎯 Use Cases

- **Dokumenten-Management**: Große Sammlungen analysieren und durchsuchen
- **Forschung**: Paper, Artikel, Notizen kategorisieren
- **Code-Analyse**: Python-Projekte, Git-Repos scannen
- **Prompt-Engineering**: Prompts und LLM-Outputs klassifizieren
- **Duplikat-Bereinigung**: Ähnliche Dokumente identifizieren

## 📄 Lizenz

Dieses Projekt ist für den persönlichen Gebrauch entwickelt.

## 🤝 Beitragen

Aktuell keine externen Contributions vorgesehen (persönliches Projekt).

## ⚠️ Hinweise

- **PDF-Support**: Benötigt `PyMuPDF` (automatisch installiert)
- **API-Kosten**: Claude Haiku 4.5 ist sehr kostengünstig (~$0.25 pro Million Tokens Input)
- **Embeddings**: Gemini Embedding-001 ist kostenlos (bis zu bestimmten Limits)
- **Performance**: Große Ordner (1000+ Dateien) können länger dauern
- **Datenbank-Größe**: Embeddings benötigen ~3KB pro Dokument

## 🔗 Links

- **GitHub**: https://github.com/Imperativ/Never-tired-archaeologist
- **Anthropic Console**: https://console.anthropic.com/
- **Google AI Studio**: https://aistudio.google.com/

## 📞 Support

Bei Fragen oder Problemen:

1. Prüfe die Logs im GUI
2. Schau in `error_log.txt` im Quellordner
3. Teste mit kleinem Ordner zuerst
4. Stelle sicher, dass API-Keys korrekt sind

---

**Version**: 3.0.0
**Letzte Aktualisierung**: Januar 2025
**Python-Version**: 3.12+
