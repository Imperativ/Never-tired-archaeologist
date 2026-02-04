# 🌐 Web-Interface Benutzerhandbuch

**Never-Tired-Archaeologist - Intelligente Dokumentensuche**

---

## 🚀 Schnellstart

### Server starten

```bash
cd Never-tired-archaeologist
.venv\Scripts\activate
python web_interface.py
```

### Im Browser öffnen

Öffnen Sie Ihren Browser und navigieren Sie zu:

```
http://localhost:5000
```

---

## ✨ Features

### 1. **Volltextsuche** 🔎
- Sucht nach Text in Dokumenten und Metadaten
- Unterstützt Teilwort-Matching
- Kombinierbar mit Sprach- und Topic-Filtern

**Beispiel:**
- Suche: `"ConfiForms"` → Findet alle Dokumente mit diesem Begriff
- Suche: `"Jira Epic"` → Findet relevante Dokumente

### 2. **Semantische Suche** 🧠
- Findet konzeptionell ähnliche Dokumente
- Nutzt KI-Embeddings (384-Dimensionen)
- Versteht Bedeutung, nicht nur Worte

**Beispiel:**
- Suche: `"Wie erstelle ich ein Confluence-Makro?"`
  → Findet Dokumente über ConfiForms, Makros, Implementierung
- Suche: `"AI prompt optimization"`
  → Findet Prompt-Engineering-Dokumente

### 3. **Filter** 🎯
- **Sprache:** Filtert nach `de`, `en`, etc.
- **Topics:** Filtert nach Hauptthemen (ConfiForms, Confluence, System Prompts, etc.)
- Kombinierbar mit Suchfunktionen

### 4. **Dokument-Details** 📄
Klicken Sie auf ein Suchergebnis, um zu sehen:
- Vollständiger Titel
- Sprache & Topics
- Zusammenfassung
- Keywords
- **Volltext-Vorschau**
- Button: "Ähnliche Dokumente finden"

### 5. **Ähnliche Dokumente** 🔗
- Findet semantisch verwandte Dokumente
- Zeigt Ähnlichkeits-Score (0-100%)
- Basiert auf Embedding-Ähnlichkeit

---

## 📊 Dashboard (Startseite)

### Statistiken
- **Dokumente:** Gesamtzahl in der Datenbank (aktuell: 124)
- **Sprachen:** Anzahl unterschiedlicher Sprachen (2: de, en)
- **Topics:** Anzahl verschiedener Themen (61)

---

## 🎨 Benutzeroberfläche

### Suchbereich
```
┌─────────────────────────────────────────────┐
│  Suche nach Dokumenten...                   │
└─────────────────────────────────────────────┘
┌────────────┐  ┌──────────────┐
│ Sprache ▼  │  │ Topics ▼     │
└────────────┘  └──────────────┘
┌────────────┐  ┌────────────┐  ┌───────────┐
│ 🔎 Textsuche│  │ 🧠 Semantik│  │ 📚 Browse │
└────────────┘  └────────────┘  └───────────┘
```

### Ergebnisliste
```
┌─────────────────────────────────────────────┐
│ Dokumenten-Titel                            │
│ [de] [ConfiForms] [Confluence] [Jira]      │
│ Zusammenfassung des Dokuments...           │
└─────────────────────────────────────────────┘
```

---

## 🔧 API-Endpunkte

Das Interface nutzt folgende REST-APIs:

### `GET /api/search`
**Volltextsuche**
```
GET /api/search?q=ConfiForms&lang=de&topic=Confluence&limit=20
```

**Response:**
```json
{
  "query": "ConfiForms",
  "total_results": 15,
  "results": [
    {
      "id": 42,
      "title": "ConfiForms-Makro Implementierung",
      "language": "de",
      "topics": ["ConfiForms", "Confluence"],
      "summary": "...",
      "snippet": "..."
    }
  ]
}
```

### `POST /api/semantic-search`
**Semantische Suche**
```json
POST /api/semantic-search
{
  "query": "Wie erstelle ich ein Makro?",
  "limit": 10
}
```

**Response:**
```json
{
  "query": "Wie erstelle ich ein Makro?",
  "total_results": 10,
  "results": [
    {
      "id": 42,
      "title": "...",
      "similarity": 0.8756
    }
  ]
}
```

### `GET /api/document/{id}`
**Dokument-Details**
```
GET /api/document/42
```

### `GET /api/similar/{id}`
**Ähnliche Dokumente**
```
GET /api/similar/42?limit=5
```

### `GET /api/browse`
**Alle durchsuchen (mit Pagination)**
```
GET /api/browse?page=1&per_page=20&lang=de&topic=ConfiForms
```

### `GET /api/stats`
**Datenbank-Statistiken**
```
GET /api/stats
```

**Response:**
```json
{
  "total_documents": 124,
  "documents_with_embeddings": 124,
  "languages": {"de": 95, "en": 21},
  "top_topics": [
    {"topic": "ConfiForms", "count": 21},
    {"topic": "Confluence", "count": 10}
  ]
}
```

---

## 💡 Anwendungsbeispiele

### Use Case 1: Alle ConfiForms-Dokumente finden
1. Setze Topic-Filter auf: `ConfiForms`
2. Klicke: **📚 Alle durchsuchen**
3. Ergebnis: 21 ConfiForms-Dokumente

### Use Case 2: Deutsche Prompt-Engineering-Dokumente
1. Setze Sprach-Filter: `de`
2. Setze Topic-Filter: `Prompt Engineering`
3. Klicke: **📚 Alle durchsuchen**

### Use Case 3: Ähnliche Lösungen finden
1. Öffne ein Dokument (z.B. "ConfiForms-Makro Implementierung")
2. Klicke: **Ähnliche Dokumente finden**
3. Ergebnis: Verwandte Implementierungen und Konzepte

### Use Case 4: Konzeptsuche
1. Gib ein: `"Wie automatisiere ich Jira Epic-Erstellung?"`
2. Klicke: **🧠 Semantische Suche**
3. Ergebnis: Alle relevanten Dokumente, auch wenn sie andere Worte verwenden

---

## 🎯 Tipps & Tricks

### Für beste Suchergebnisse:

**Textsuche:**
- Nutze spezifische Keywords: `"ConfiForms Makro"` statt `"Makro"`
- Kombiniere mit Filtern für präzise Ergebnisse
- Gut für bekannte Begriffe und Eigennamen

**Semantische Suche:**
- Stelle Fragen in natürlicher Sprache
- Beschreibe das Konzept, nicht nur Keywords
- Ideal für: "Ich suche etwas Ähnliches wie..."
- Beispiel: `"Dokumentation zur Jira-Integration"` findet auch ConfiForms-Docs

### Filter effektiv nutzen:
- **Sprache:** Bei mehrsprachigen Projekten essentiell
- **Topics:** Reduziert Ergebnisse auf relevante Bereiche
- Kombiniere beide für maximale Präzision

### Performance-Hinweise:
- **Erste semantische Suche:** ~3 Sekunden (Embedding-Modell laden)
- **Weitere semantische Suchen:** ~1 Sekunde
- **Textsuche:** <100ms
- **Browse-Modus:** Instant

---

## 🔍 Erweiterte Nutzung

### Ähnlichkeits-Scores interpretieren:
- **90-100%:** Nahezu identisch (z.B. Duplikate, Versionen)
- **80-90%:** Sehr ähnlich (gleiche Thematik, andere Perspektive)
- **70-80%:** Verwandt (ähnliche Konzepte)
- **60-70%:** Locker verwandt
- **<60%:** Schwach verwandt

### Multi-Step-Recherche:
1. **Breite Suche:** Semantisch nach Konzept suchen
2. **Bestes Ergebnis öffnen:** Details ansehen
3. **Ähnliche finden:** Verwandte Dokumente entdecken
4. **Iteration:** Weitere ähnliche Dokumente explorieren

---

## 🛠️ Troubleshooting

### Server startet nicht
**Problem:** Port 5000 bereits belegt

**Lösung:** Ändere Port in `web_interface.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5001)
```

### Semantische Suche langsam
**Problem:** Embedding-Modell wird bei jeder Suche neu geladen

**Hinweis:** Das ist normal beim ersten Mal. Danach bleibt es im RAM geladen.

### Keine Ergebnisse bei semantischer Suche
**Problem:** Dokumente haben keine Embeddings

**Lösung:** Prüfe mit `/api/stats`, ob `documents_with_embeddings > 0`

### Browser kann Server nicht erreichen
**Problem:** Firewall blockiert Port 5000

**Lösung:**
1. Windows Firewall öffnen
2. Erlaube Python-Zugriff auf Port 5000
3. Oder: Nutze `http://127.0.0.1:5000` statt `localhost`

---

## 📊 Datenbank-Info

### Aktuelle Inhalte (Stand: 2026-02-02)
- **124 Dokumente** in der Datenbank
- **95 deutsche** und **21 englische** Dokumente
- **61 verschiedene Topics**
- **124 Embeddings** (384 Dimensionen)

### Top Topics:
1. ConfiForms (21)
2. Confluence (10)
3. System Prompts (5+6 = 11)
4. Prompt Engineering (4)
5. Jira Integration (4)

---

## 🚦 Status-Anzeige

Während der Benutzung sehen Sie:
- **⏳ Lade Ergebnisse...** - Server verarbeitet Anfrage
- **Keine Ergebnisse gefunden** - Suchkriterien zu spezifisch
- **X Ergebnisse** - Erfolgreiche Suche

---

## 🔐 Sicherheitshinweise

⚠️ **Lokaler Betrieb empfohlen:**
- Das Interface ist für lokalen Betrieb konzipiert
- Keine Authentifizierung implementiert
- **Nicht ohne Anpassungen im Internet deployen!**

### Für Produktiv-Einsatz:
- [ ] Authentifizierung hinzufügen
- [ ] HTTPS aktivieren
- [ ] Rate-Limiting implementieren
- [ ] Zugriffskontrolle einrichten

---

## 📞 Support & Feedback

Bei Fragen oder Problemen:
1. Check `web_interface.log` für Fehler-Details
2. Prüfe Browser-Konsole (F12) für Client-Fehler
3. GitHub Issue erstellen mit:
   - Fehlerbeschreibung
   - Log-Auszüge
   - Browser & Version

---

## 🎉 Viel Erfolg beim Durchsuchen Ihrer Dokumente!

**Tipp:** Experimentieren Sie mit der semantischen Suche - sie findet oft überraschend relevante Dokumente, die Textsuche übersehen würde! 🚀
