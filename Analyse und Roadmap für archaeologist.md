<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# [https://github.com/Imperativ/Never-tired-archaeologist](https://github.com/Imperativ/Never-tired-archaeologist) lies dir dieses gitprojekt gründlich durch und mach dich vollständig mit den sachlichen und fachlichen inhalten vertraut. dann möchte ich dass du den ist-stand feststellst und vor allem, wie weit dieser noch von einem produktivstand entfernt ist. Daraus erstelle bitte eine roadmap, wie du vorgehen willst um nach und nach das ganze projekt zu einem erfolg werden zu lassen.

Basierend auf meiner gründlichen Analyse des Projekts "Never-tired-archaeologist" kann ich dir nun eine umfassende Bewertung des Ist-Zustands und eine detaillierte Roadmap zur Produktreife präsentieren.

## Ist-Zustand-Analyse

### Aktuelle Stärken

**Kernfunktionalität vorhanden (70% fertig)**

- ✅ Funktionierende Tkinter-GUI auf Deutsch
- ✅ Rekursiver Dateiscan für 7 Dateitypen (.txt, .md, .pdf, .py, .json, .csv, .html)
- ✅ OpenAI GPT-Integration für Metadatenanalyse (gpt-4o-mini)
- ✅ Embedding-Generierung (text-embedding-3-large)
- ✅ Duplikaterkennung über Cosine-Similarity
- ✅ Markdown-Export mit YAML-Headern
- ✅ Fehlerprotokollierung
- ✅ Modulare Architektur (gut strukturiert in 7 Module)

**Code-Qualität**

- ✅ Saubere Modultrennung (analyzer, exporter, scanner, etc.)
- ✅ UTF-8-Encoding durchgängig
- ✅ Basis-Fehlerbehandlung vorhanden
- ✅ .env-Datei für API-Key-Verwaltung


### Kritische Schwachstellen (Distanz zur Produktreife)

**1. Keine Tests (❌ 0%)**

- Keine Unit-Tests
- Keine Integration-Tests
- Keine Test-Coverage
- Keine CI/CD-Pipeline

**2. Unvollständige Fehlerbehandlung (⚠️ 40%)**

- `analyzer_fixed.py` enthält nur "\# kommt bald" (funktionslos)
- Backup-Dateien (.backup, .backup2, .original) im Repository (unprofessionell)
- Keine strukturierte Exception-Hierarchie
- Keine Logging-Strategie (nur einfache Textdateien)

**3. Fehlende Produktionsfeatures (⚠️ 20%)**

- Keine Konfigurationsdatei (alles hardcoded)
- Kein Fortschrittsbalken für große Scans
- Keine Abbruch-Funktion während Verarbeitung
- Keine Batch-Verarbeitung oder Parallelisierung
- Keine Ratenbegrenzung für OpenAI API (Kostenfalle!)
- Keine Offline-Modus-Option

**4. Skalierbarkeit \& Performance (⚠️ 30%)**

- Alle Embeddings im RAM (keine Persistierung)
- Keine Datenbankanbindung
- Bei 1000+ Dateien: Memory-Probleme vorprogrammiert
- Keine Caching-Strategie für bereits analysierte Dateien

**5. UX/UI-Mängel (⚠️ 50%)**

- Sehr spartanisches GUI
- Keine Vorschau der zu scannenden Dateien
- Keine Statistiken (Kosten, Zeit, Dateigröße)
- Keine Export-Format-Optionen (nur Markdown)
- Keine Suchfunktion in verarbeiteten Ergebnissen

**6. Dokumentation (⚠️ 40%)**

- README ist basic (Installation + Start)
- Keine API-Dokumentation
- Keine Architektur-Diagramme
- Keine Beispiel-Outputs
- Keine Troubleshooting-Sektion

**7. Security \& Compliance (❌ 10%)**

- API-Key-Validierung fehlt
- Keine Input-Sanitierung
- Keine Datenschutz-Hinweise (DSGVO!)
- Keine Verschlüsselung sensibler Metadaten

**8. Deployment (❌ 0%)**

- Keine Packaging (PyPI, Homebrew, etc.)
- Keine Docker-Container
- Keine Installatoren (Windows .exe, macOS .app)
- Keine Auto-Update-Mechanismus


### Beurteilung: **Entfernung zur Produktreife**

```
Aktueller Stand:     ████████░░░░░░░░░░░░ 40% (Early Alpha)
Produktionsreife:    ████████████████████ 100%

Geschätzte Distanz:  6-9 Monate Entwicklungszeit (bei 1 FTE)
```


***

## 🚀 Roadmap zur Produktionsreife

### Phase 1: Stabilisierung \& Code-Hygiene (4-6 Wochen)

**Priorität: KRITISCH**

#### Sprint 1.1: Repository-Cleanup (Woche 1)

- [ ] Alle .backup/.original-Dateien löschen
- [ ] `.gitignore` erweitern (`.env`, `_processed/`, `__pycache__/`, `.pytest_cache/`)
- [ ] `analyzer_fixed.py` entweder implementieren oder löschen
- [ ] Commit-Historie bereinigen (sensible Daten?)
- [ ] Branch-Strategie etablieren (main, develop, feature/*)


#### Sprint 1.2: Test-Infrastruktur (Woche 2-3)

```python
# Neue Struktur
tests/
├── unit/
│   ├── test_analyzer.py
│   ├── test_dupdetect.py
│   ├── test_text_extractor.py
│   └── test_exporter.py
├── integration/
│   ├── test_full_pipeline.py
│   └── test_api_integration.py
└── fixtures/
    ├── sample.pdf
    ├── sample.md
    └── test_documents/
```

**Zu implementieren:**

- pytest-Setup mit Fixtures
- Mock für OpenAI API (keine echten Calls in Tests)
- Test-Coverage mindestens 80%
- GitHub Actions für CI (pytest + linting)


#### Sprint 1.3: Fehlerbehandlung (Woche 3-4)

```python
# Neue Exception-Hierarchie
class ArchaeologistError(Exception): pass
class APIError(ArchaeologistError): pass
class FileProcessingError(ArchaeologistError): pass
class EmbeddingError(ArchaeologistError): pass
```

- Structured Logging (loguru statt print)
- Retry-Logik für API-Calls
- Graceful Degradation (z.B. ohne Embeddings weiterarbeiten)


#### Sprint 1.4: Konfiguration (Woche 4)

```yaml
# config.yaml
api:
  provider: openai
  model_analysis: gpt-4o-mini
  model_embedding: text-embedding-3-large
  rate_limit: 60  # requests/minute
  timeout: 30
  
processing:
  max_file_size_mb: 50
  supported_extensions: [.txt, .md, .pdf, .py, .json, .csv, .html]
  batch_size: 10
  
similarity:
  threshold: 0.95
  enable_by_default: true
  
export:
  format: markdown
  include_embeddings: false  # Zu groß für YAML
```

**Deliverables Phase 1:**

- ✅ Clean Repository
- ✅ 80%+ Test-Coverage
- ✅ CI/CD-Pipeline läuft
- ✅ Robustes Error-Handling
- ✅ Konfigurierbarkeit

***

### Phase 2: Feature-Completeness (6-8 Wochen)

**Priorität: HOCH**

#### Sprint 2.1: Datenpersistierung (Woche 5-6)

```python
# SQLite-Integration
database/
├── schema.sql
└── models.py

# Tabellen:
# - documents (id, filepath, hash, processed_at)
# - embeddings (doc_id, vector_blob, model_version)
# - metadata (doc_id, key, value)
# - duplicates (doc_id, duplicate_of_id, similarity)
```

**Features:**

- Inkrementelle Scans (nur neue/geänderte Dateien)
- Embedding-Cache (nicht jedes Mal neu berechnen)
- Query-Interface für verarbeitete Dokumente
- Export-Historie


#### Sprint 2.2: API-Kostenmanagement (Woche 6-7)

```python
# Neue Komponente: cost_tracker.py
class CostTracker:
    def estimate_cost(self, text_length, use_embeddings):
        # GPT-4o-mini: $0.15/1M input tokens
        # Embeddings: $0.13/1M tokens
        pass
    
    def track_usage(self):
        # Persistiert Kosten pro Run
        pass
    
    def get_budget_alert(self, max_cost):
        # Warnung wenn Budget überschritten
        pass
```

**Features:**

- Kostenvorschau vor dem Scan
- Budget-Limits (abbruch wenn überschritten)
- Detaillierte Kostenaufschlüsselung im Logfile
- Caching-Strategie (gleicher Text = kein erneuter API-Call)


#### Sprint 2.3: Performance-Optimierung (Woche 7-8)

```python
# Parallelisierung mit asyncio
async def process_files_batch(files, batch_size=10):
    # 10 Dateien parallel verarbeiten
    pass

# Streaming für große PDFs
def extract_text_streaming(pdf_path):
    # Nicht komplette Datei in RAM
    pass
```

**Features:**

- Multithreading für I/O-bound Operationen
- Async OpenAI-Calls
- Memory-effizientes PDF-Processing
- Progress-Tracking mit tqdm


#### Sprint 2.4: Export-Optionen (Woche 8-9)

```python
# Neue Exporter
exporters/
├── markdown_exporter.py  # Bestehend
├── json_exporter.py      # Neu
├── csv_exporter.py       # Neu
└── html_exporter.py      # Neu (schöne Visualisierung)
```

**Features:**

- JSON-Export (maschinenlesbar)
- CSV-Export (für Excel/Tabellen)
- HTML-Report (Statistiken + Visualisierungen)
- Deduplizierter Export (nur Originale, keine Duplikate)

**Deliverables Phase 2:**

- ✅ Persistente Datenhaltung (SQLite)
- ✅ Inkrementelle Scans
- ✅ Kosten-Tracking \& Budgets
- ✅ 3-5x schnellere Verarbeitung
- ✅ Flexible Export-Formate

***

### Phase 3: User Experience (4-6 Wochen)

**Priorität: MITTEL-HOCH**

#### Sprint 3.1: GUI-Überarbeitung (Woche 10-11)

```python
# Moderne GUI mit customtkinter
import customtkinter as ctk

# Neue Features:
# - Dark Mode
# - Fortschrittsbalken mit ETA
# - Live-Vorschau verarbeiteter Dateien
# - Abbruch-Button
# - Statistik-Dashboard
```

**Wireframe:**

```
┌─────────────────────────────────────────────────┐
│  Archaeologist v2.0.0        [─] [□] [×]       │
├─────────────────────────────────────────────────┤
│  📁 Quellordner: /Users/...   [Durchsuchen]    │
│  📊 Gefunden: 234 Dateien (45 MB)              │
├─────────────────────────────────────────────────┤
│  ⚙️ Einstellungen:                              │
│    ☑ Embeddings erzeugen                        │
│    ☑ Duplikaterkennung (>95% Ähnlichkeit)     │
│    ☐ Nur neue/geänderte Dateien               │
│    Export: [Markdown ▼]                        │
├─────────────────────────────────────────────────┤
│  💰 Geschätzte Kosten: ~$2.34                  │
│  ⏱️ Geschätzte Dauer: ~8 Min                   │
│                                                 │
│  [▶ Scannen starten]  [⏸ Abbrechen]          │
│                                                 │
│  Progress: ████████░░░░ 67% (157/234)         │
│            Verarbeite: document_xyz.pdf        │
├─────────────────────────────────────────────────┤
│  📋 Log:                                        │
│  [Scrollbarer Bereich mit farbigen Logs]      │
└─────────────────────────────────────────────────┘
```


#### Sprint 3.2: CLI-Modus (Woche 11-12)

```bash
# Für Power-User & Scripting
archaeologist scan ./docs --format json --no-embeddings
archaeologist query "Finde alle Python-Dateien" --output results.csv
archaeologist dedupe --threshold 0.90 --dry-run
```

**Tool:** Click oder Typer für CLI
**Features:**

- Vollständige CLI-Alternative zur GUI
- Skriptfähig \& automatisierbar
- Batch-Verarbeitung
- JSON-Output für Pipelines


#### Sprint 3.3: Reporting \& Analytics (Woche 12-13)

```python
# HTML-Dashboard mit Charts
from plotly import graph_objects as go

# Visualisierungen:
# - Dateitypen-Verteilung (Pie Chart)
# - Duplikate-Cluster (Network Graph)
# - Sprachen-Verteilung
# - Timeline (wann wurden Dateien erstellt)
# - Keyword-Cloud
```

**Deliverables Phase 3:**

- ✅ Moderne, intuitive GUI
- ✅ CLI-Modus für Automation
- ✅ Interaktive HTML-Reports
- ✅ Abbruch-Funktion
- ✅ Live-Statistiken

***

### Phase 4: Enterprise-Ready (6-8 Wochen)

**Priorität: MITTEL**

#### Sprint 4.1: Multi-Provider-Support (Woche 14-15)

```python
# Provider-Abstraction
providers/
├── openai_provider.py
├── anthropic_provider.py  # Claude
├── local_provider.py      # Ollama/llama.cpp
└── azure_provider.py      # Azure OpenAI
```

**Features:**

- Austauschbare LLM-Backends
- Lokale Modelle (offline-fähig)
- Vendor-Lock-in vermeiden
- Kostenvergleich zwischen Providern


#### Sprint 4.2: Plugin-System (Woche 15-16)

```python
# Erweiterbarkeit
plugins/
├── __init__.py
├── docx_reader.py     # Word-Dokumente
├── xlsx_reader.py     # Excel-Dateien
├── email_parser.py    # .eml/.msg
└── custom_analyzer.py # Nutzer-definierte Analysen
```

**Features:**

- Plugin-API für Custom-Extraktoren
- Marketplace (später)
- Hot-Loading von Plugins


#### Sprint 4.3: Security \& Compliance (Woche 16-17)

```python
# security/
├── encryption.py      # Verschlüsselte Metadaten-Speicherung
├── audit_log.py       # Wer hat was wann verarbeitet
└── pii_detector.py    # PII-Erkennung (DSGVO)
```

**Features:**

- Verschlüsselung von Embeddings (optional)
- Audit-Trail für Compliance
- PII-Warnung (z.B. Kreditkarten-Nummern in Dokumenten)
- DSGVO-Konformität


#### Sprint 4.4: Deployment-Optionen (Woche 17-18)

```dockerfile
# Docker-Support
FROM python:3.11-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
services:
  archaeologist:
    build: .
    volumes:
      - ./documents:/data/input
      - ./processed:/data/output
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

**Features:**

- Docker-Image (Linux/Mac/Windows)
- Standalone-Binaries (PyInstaller)
- Homebrew-Formula (macOS)
- Snap/Flatpak (Linux)
- Windows-Installer (.msi)

**Deliverables Phase 4:**

- ✅ Multi-Provider-Support
- ✅ Plugin-Architektur
- ✅ Security-Audit bestanden
- ✅ Container + Binaries

***

### Phase 5: Productization (4-6 Wochen)

**Priorität: NIEDRIG-MITTEL**

#### Sprint 5.1: Dokumentation (Woche 19-20)

```
docs/
├── README.md              # Überarbeitet, ausführlich
├── QUICKSTART.md
├── ARCHITECTURE.md
├── API_REFERENCE.md
├── TROUBLESHOOTING.md
├── CONTRIBUTING.md
└── examples/
    ├── basic_usage.py
    ├── cli_scripting.sh
    └── plugin_development.md
```


#### Sprint 5.2: Website \& Marketing (Woche 20-21)

- Landing-Page (Jekyll/Hugo)
- Video-Tutorial (YouTube)
- Blogpost: "Why I built this"
- Social-Media-Präsenz


#### Sprint 5.3: Community-Building (Woche 21-22)

- GitHub-Discussions aktivieren
- Discord-Server
- Contributing-Guidelines
- Issue-Templates
- PR-Templates
- Code-of-Conduct


#### Sprint 5.4: Monitoring \& Analytics (Woche 22-23)

```python
# Optional: Telemetrie (opt-in!)
from telemetry import track_event

track_event("scan_completed", {
    "file_count": 234,
    "duration_seconds": 480,
    "embeddings_enabled": True
})
```

**Features:**

- Opt-in Telemetrie (anonymisiert)
- Crash-Reporting (Sentry)
- Update-Notifications
- Feature-Usage-Tracking

**Deliverables Phase 5:**

- ✅ Vollständige Dokumentation
- ✅ Website + Demo
- ✅ Community-Infrastruktur
- ✅ Monitoring-Setup

***

## Priorisierte Action-Items (Start HEUTE)

### Quick Wins (Diese Woche)

1. **Repository aufräumen** (2h)

```bash
git rm *.backup *.backup2 *.original
git commit -m "chore: remove backup files"
```

2. **Requirements erweitern** (1h)

```txt
# requirements.txt
openai>=1.40.0
python-dotenv>=1.0.1
PyMuPDF>=1.24.10
pyyaml>=6.0          # NEU: Config-Files
loguru>=0.7.0        # NEU: Logging
tqdm>=4.66.0         # NEU: Progress-Bars
pytest>=8.0.0        # NEU: Testing
```

3. **GitHub Actions CI** (2h)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=. --cov-report=xml
```

4. **Erste Tests schreiben** (4h)

```python
# tests/unit/test_dupdetect.py
def test_cosine_sim_identical():
    vec = [1.0, 2.0, 3.0]
    assert cosine_sim(vec, vec) == 1.0

def test_cosine_sim_orthogonal():
    assert cosine_sim([1, 0], [0, 1]) == 0.0
```

5. **Logging einbauen** (3h)

```python
from loguru import logger

# Statt print():
logger.info(f"Processing {file_path}")
logger.error(f"Failed to parse {file_path}: {e}")
```


***

## Erfolgsmetriken

### Alpha-Release (3 Monate)

- [ ] 80% Test-Coverage
- [ ] CI/CD läuft grün
- [ ] 0 kritische Bugs
- [ ] SQLite-Integration
- [ ] Kosten-Tracking
- [ ] 10 Beta-Tester


### Beta-Release (6 Monate)

- [ ] 90% Test-Coverage
- [ ] Performance: 100+ Dateien/Min
- [ ] 3 Export-Formate
- [ ] Multi-Provider-Support
- [ ] 100+ GitHub-Stars
- [ ] 5 Contributors


### 1.0 Production (9 Monate)

- [ ] Security-Audit bestanden
- [ ] Docker + Binaries verfügbar
- [ ] Vollständige Docs
- [ ] 500+ GitHub-Stars
- [ ] 20+ Contributors
- [ ] Featured auf "Awesome Lists"

***

## Ressourcenbedarf

### Solo-Entwickler (Du alleine)

- **Zeitaufwand:** 15-20h/Woche
- **Dauer:** 9-12 Monate
- **Kosten:** ~\$200 für OpenAI API während Entwicklung


### Mit Team (2-3 Entwickler)

- **Zeitaufwand:** 10-15h/Woche pro Person
- **Dauer:** 4-6 Monate
- **Kosten:** ~\$500 (API + CI/CD + Hosting)

***

## Fazit

**Aktueller Stand:** Das Projekt hat ein **solides Fundament** mit funktionierender Kernlogik, aber **deutliche Lücken** in Test-Coverage, Performance, UX und Produktionsreife.

**Größte Baustellen:**

1. ❌ Keine Tests
2. ⚠️ Performance-Probleme bei Skalierung
3. ⚠️ Keine Kosten-Kontrolle
4. ⚠️ Spartanische UX

**Potenzial:** Mit strukturierter Arbeit **absolut realistisch in 6-9 Monaten produktionsreif**. Der Markt für Document-AI-Tools wächst stark (siehe Recherche: Docling, OmniDocBench), dein Tool hat mit Duplikaterkennung ein **Alleinstellungsmerkmal**.

**Nächster Schritt:** Starte mit **Phase 1 (Stabilisierung)** – cleanes Repo, Tests, CI/CD. Das ist die Basis für alles Weitere.

Soll ich dir bei einem spezifischen Teil der Roadmap mit konkretem Code helfen?
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^2][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/Imperativ/Never-tired-archaeologist

[^2]: https://onlinelibrary.wiley.com/doi/10.1111/fire.12387

[^3]: https://www.sachetas.in/index.php/Sachetas/article/view/295

[^4]: https://ieeexplore.ieee.org/document/10816957/

[^5]: https://www.nepjol.info/index.php/shaheedsmriti/article/view/76808

[^6]: https://ijsrem.com/download/a-study-on-cost-control-practices-at-dr-reddys-laboratories-hyderabad/

[^7]: https://link.springer.com/10.1007/s11042-024-19185-w

[^8]: https://journal.formosapublisher.org/index.php/fjas/article/view/11469

[^9]: https://oftalmoloji.org/articles/turkish-retinoblastoma-research-a-bibliometric-analysis-1966-2024/doi/tjo.galenos.2024.43247

[^10]: https://www.jippublication.com/index.php/jip/article/view/890

[^11]: https://jurnal.ympn2.or.id/index.php/JLPS/article/view/39

[^12]: https://arxiv.org/html/2412.07626v2

[^13]: https://arxiv.org/pdf/2111.08609.pdf

[^14]: https://arxiv.org/pdf/2501.17887.pdf

[^15]: https://arxiv.org/html/2406.11633v1

[^16]: http://arxiv.org/pdf/2408.09869.pdf

[^17]: https://arxiv.org/abs/2407.10701

[^18]: https://arxiv.org/pdf/2310.12430.pdf

[^19]: https://arxiv.org/abs/2410.12628

[^20]: https://www.marketsandmarkets.com/Market-Reports/document-processing-ai-market-87883040.html

[^21]: https://idp-software.com/news/2025-11-news/

[^22]: https://complexdiscovery.com/category/market-sizing/

[^23]: https://www.globenewswire.com/news-release/2025/12/04/3199917/0/en/Data-Pipeline-Tools-Market-to-Surpass-USD-66-18-Billion-by-2033-Driven-by-Rising-Data-Volumes-and-Real-Time-Processing-Needs-SNS-Insider.html

[^24]: https://scoop.market.us/subscription-scanning-market-news/

[^25]: https://community.databricks.com/t5/technical-blog/how-to-perform-semantic-search-in-databricks-lakebase/ba-p/139846

[^26]: https://github.com/Kludex/awesome-pydantic/blob/main/README.md

[^27]: https://futurumgroup.com

[^28]: https://arxiv.org/html/2512.03514v1

[^29]: https://planetpython.org

