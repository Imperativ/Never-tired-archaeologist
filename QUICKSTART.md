# 🚀 Never-tired-archaeologist - Quick Start Guide

**Schnelle Demo-Installation in 5 Minuten!**

---

## 📋 Voraussetzungen

- **Windows 10/11**
- **Python 3.12** (wird automatisch installiert falls nicht vorhanden)
- **Internet-Verbindung**

---

## ⚡ Option 1: Automatische Installation (Empfohlen!)

### Schritt 1: Repository klonen

```bash
git clone https://github.com/Imperativ/Never-tired-archaeologist.git
cd Never-tired-archaeologist
```

### Schritt 2: Setup-Script ausführen

```bash
setup.bat
```

Das war's! Das Script:
- ✅ Prüft Python 3.12
- ✅ Erstellt Virtual Environment
- ✅ Installiert alle Dependencies
- ✅ Startet die App automatisch

---

## 🔧 Option 2: Manuelle Installation

### Schritt 1: Python 3.12 installieren

Falls noch nicht installiert:

```bash
winget install Python.Python.3.12
```

### Schritt 2: Repository klonen

```bash
git clone https://github.com/Imperativ/Never-tired-archaeologist.git
cd Never-tired-archaeologist
```

### Schritt 3: Virtual Environment erstellen

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### Schritt 4: Dependencies installieren

```bash
pip install -r requirements.txt
```

### Schritt 5: App starten

```bash
python main.py
```

---

## 🔑 API-Keys konfigurieren (für echte Analyse)

### Quick-Setup:

1. Kopiere `.env.example` zu `.env`:
   ```bash
   copy .env.example .env
   ```

2. Öffne `.env` und trage deine Keys ein:
   ```env
   ANTHROPIC_API_KEY=sk-ant-dein-key-hier
   GOOGLE_API_KEY=AIza-dein-key-hier
   ```

### API-Keys bekommen:

- **Anthropic (Claude):** https://console.anthropic.com/
- **Google AI (Gemini):** https://aistudio.google.com/app/apikey

**💡 Tipp:** Für eine schnelle Demo kannst du temporär die Keys vom Projekt-Owner verwenden!

---

## 🎮 Demo-Modus (ohne API-Keys)

**Möchtest du nur die GUI zeigen?**

1. Starte die App normal: `python main.py`
2. Wähle einen Ordner aus
3. Die GUI zeigt alle Features (Suche, Statistiken, etc.)
4. Beim Scannen kommt eine API-Key-Warnung (erwartet!)

**Demo-Trick:** Bereite vorher eine Demo-Datenbank vor:
- Kopiere `archaeologist.db` aus einem anderen Ordner
- Starte die App und zeige Suche + Statistiken

---

## 📁 Demo-Dokumente (mitgeliefert)

Im Ordner `demo_documents/` findest du Beispiel-Dateien:

```
demo_documents/
├── sample_code.py          # Python-Datei
├── documentation.md        # Markdown-Dokumentation
├── research_paper.pdf      # PDF-Dokument
├── data.json              # JSON-Datei
└── notes.txt              # Text-Notizen
```

**So testest du:**
1. Starte die App
2. Wähle `demo_documents/` Ordner aus
3. Klicke "Scannen & Analysieren"
4. Warte ~30 Sekunden
5. Nutze die Suche: "Python" oder "research"
6. Klicke auf "Statistiken anzeigen"

---

## 🎯 Beeindruckende Features zeigen

### 1. **Volltext-Suche** 🔍
```
Suche: "Python AND tutorial"
Suche: "machine learning"
Suche: "project OR documentation"
```

### 2. **Statistiken** 📊
- Zeigt Sprachen-Verteilung
- Dateitypen-Analyse
- Duplikate-Erkennung

### 3. **Metadaten-Extraktion** 🤖
- Automatische Sprach-Erkennung
- Topic-Klassifizierung
- Keyword-Extraktion
- Zusammenfassungen

### 4. **Duplikaterkennung** 🔄
- Findet ähnliche Dokumente
- Cosine-Similarity ≥ 0.95
- Zeigt in Statistiken

---

## 🐛 Troubleshooting

### Problem: "Python nicht gefunden"

**Lösung:**
```bash
winget install Python.Python.3.12
```

### Problem: "ANTHROPIC_API_KEY nicht gesetzt"

**Lösung 1 (schnell für Demo):**
- App startet trotzdem, nur Analyse funktioniert nicht
- Zeige GUI-Features, Suche mit vorhandener DB

**Lösung 2 (für echte Nutzung):**
- `.env` Datei erstellen und Keys eintragen

### Problem: "Module not found"

**Lösung:**
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Problem: Tests laufen nicht

**Lösung:**
```bash
python -m pytest tests/ -v
```

---

## 💡 Pro-Tipps für die Demo

### 1. **Vorbereitung (5 Minuten vorher)**

```bash
# Demo-Dokumente scannen und DB vorbereiten
python main.py
# → Ordner wählen: demo_documents/
# → Scannen lassen
# → App schließen
```

Jetzt hast du eine fertige DB mit Daten!

### 2. **Während der Demo**

```bash
# App starten
python main.py

# Zeige:
1. GUI-Übersicht erklären
2. "Statistiken anzeigen" klicken → Wow-Effekt! 📊
3. Suche demonstrieren: "Python" → Ergebnisse erscheinen
4. Optional: Neuen Ordner scannen (wenn API-Keys da sind)
```

### 3. **Beeindruckende Talking Points**

- 🚀 "7 Dateiformate unterstützt (PDF, MD, TXT, PY, JSON, CSV, HTML)"
- 🤖 "Claude AI extrahiert automatisch Metadaten"
- 🔍 "SQLite + FTS5 für blitzschnelle Volltextsuche"
- 🎯 "Duplikaterkennung via Embeddings & Cosine-Similarity"
- 📊 "Persistente Datenbank - einmal scannen, immer durchsuchbar"
- ⚡ "214 Unit-Tests, 100% Coverage"

---

## 📺 Demo-Script (30 Sekunden)

```
1. [App öffnen]
   "Das ist Never-tired-archaeologist - ein intelligentes Dokumenten-Management-Tool"

2. [Statistiken zeigen]
   "Hier seht ihr die Analyse von X Dokumenten..."
   → Sprachen, Dateitypen, Duplikate

3. [Suche demonstrieren]
   "Volltext-Suche mit FTS5..."
   → "Python" eingeben → Ergebnisse zeigen

4. [Scan zeigen]
   "Neuer Ordner? Einfach auswählen und scannen..."
   → Optional: Live-Scan demonstrieren

5. [Wow-Moment]
   "Claude AI extrahiert automatisch: Sprache, Topic, Keywords, Zusammenfassung!"
```

---

## 🎁 Bonus: Demo-Datenbank vorbereiten

**Möchtest du eine vorgefertigte Demo-DB?**

```bash
# Auf deinem Rechner:
1. Scanne interessante Ordner (z.B. ein Git-Repo)
2. Kopiere die archaeologist.db
3. Sende sie deinem Kollegen

# Beim Kollegen:
1. DB in Projekt-Ordner legen
2. App starten
3. Sofort Suche + Statistiken verfügbar!
```

---

## 📞 Support

**Fragen? Probleme?**

1. GitHub Issues: https://github.com/Imperativ/Never-tired-archaeologist/issues
2. README.md anschauen (vollständige Dokumentation)
3. MIGRATION_PYTHON312.md (technische Details)

---

## ⏱️ Zeit-Plan

```
┌─────────────────────────────────────┐
│ KOMPLETTE DEMO IN 5 MINUTEN         │
├─────────────────────────────────────┤
│ T+0:  setup.bat ausführen (2 min)   │
│ T+2:  App startet automatisch       │
│ T+3:  Demo-Ordner scannen (1 min)   │
│ T+4:  Features zeigen (1 min)       │
│ T+5:  Wow-Effekt erreicht! 🎉      │
└─────────────────────────────────────┘
```

---

**Viel Erfolg bei der Demo! 🚀**

*Never-tired-archaeologist v3.0 - Powered by Claude Haiku 4.5 & Gemini*
