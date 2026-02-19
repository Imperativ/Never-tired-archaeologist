# Testing Guide: Never-Tired-Archaeologist

**Ziel:** Validierung der Pipeline-Robustheit vor Produktiveinsatz

---

## 🚀 Schnellstart: Batch-Test ausführen

### Voraussetzungen
1. Virtuelle Umgebung aktiviert
2. `.env` Datei mit `ANTHROPIC_API_KEY` konfiguriert
3. Dependencies installiert (`pip install -r requirements.txt`)

### Test-Suite ausführen

```bash
# Batch-Test mit automatischer Erstellung von Test-Dokumenten
python batch_test.py
```

**Was passiert:**
- 7 diverse Test-Dokumente werden erstellt (falls nicht vorhanden)
- Jedes Dokument wird durch die komplette Pipeline verarbeitet
- Ergebnisse werden in `batch_test.log` und `batch_test_results.json` gespeichert
- Exit-Code 0 = alle Tests erfolgreich, 1 = mindestens ein Fehler

---

## 📋 Test-Dokumente

Der Batch-Test erstellt automatisch folgende Test-Dokumente:

| Datei | Zweck | Besonderheit |
|-------|-------|--------------|
| `test_01_short_english.txt` | Kurzer englischer Text | Baseline-Test |
| `test_02_long_german.txt` | Langer deutscher Text | Testet Textlänge, deutsche Sprache |
| `test_03_technical_code.txt` | Technische Dokumentation | Markdown, Code-Snippets |
| `test_04_multilingual.txt` | Mehrsprachiger Text | EN, FR, DE gemischt |
| `test_05_scientific.txt` | Wissenschaftlicher Text | Fachterminologie, Struktur |
| `test_06_short_list.txt` | Sehr kurzer Text | Minimalfall, Listen |
| `test_07_special_chars.txt` | Unicode/Emoji | Sonderzeichen, Emoji, Umlaute |

---

## 🎯 Erfolgs-Kriterien

Ein erfolgreicher Test erfüllt:
- ✅ **Success Rate ≥ 85%** (mindestens 6 von 7 Dokumenten)
- ✅ **Durchschnittliche Verarbeitungszeit < 10s** pro Dokument
- ✅ **Keine kritischen Fehler** (z.B. Encoding, API-Timeouts)
- ✅ **Metadaten sind sinnvoll** (Titel, Sprache, Keywords plausibel)

---

## 📊 Ergebnisse interpretieren

### Konsolen-Ausgabe
```
============================================================
BATCH TEST SUMMARY
============================================================
Total Documents:      7
Successful:           6 ✓
Failed:               1 ✗
Success Rate:         85.7%
Total Processing Time: 42.3s
Avg Processing Time:  6.04s
Avg Content Length:   450 chars
============================================================
```

### JSON-Export (`batch_test_results.json`)
Enthält detaillierte Informationen zu jedem Dokument:
- Verarbeitungszeit
- Extrahierte Metadaten
- Fehler (falls aufgetreten)
- Embedding-Dimension

---

## 🔍 Manuelle Einzeltests

### Einzelnes Dokument testen
```bash
python main.py test_documents/test_01_short_english.txt
```

### Duplikat-Check testen
```bash
# Erstes Mal: sollte verarbeitet werden
python main.py test_documents/test_01_short_english.txt

# Zweites Mal: sollte Duplikat erkennen
python main.py test_documents/test_01_short_english.txt
```

### Force-Reprocessing testen
```bash
# Duplikat-Check überspringen
python main.py test_documents/test_01_short_english.txt --force
```

---

## 🧪 Eigene Test-Dokumente hinzufügen

1. **Erstelle Datei** in `test_documents/`:
   ```bash
   echo "Dein Test-Inhalt" > test_documents/mein_test.txt
   ```

2. **Führe Batch-Test erneut aus**:
   ```bash
   python batch_test.py
   ```

3. **Oder teste einzeln**:
   ```bash
   python main.py test_documents/mein_test.txt
   ```

---

## 🐛 Häufige Probleme & Lösungen

### Problem: "Model not found" (404 Error)
**Symptom:** Claude API gibt 404-Fehler zurück

**Lösung:**
```python
# In src/llm.py Zeile 30 ändern zu:
model: str = "claude-sonnet-4"  # Version-agnostic
```

---

### Problem: Langsame Embedding-Generierung (>5s)
**Symptom:** "Loading embedding model" dauert sehr lange

**Lösung:** HuggingFace Token setzen
```bash
# In .env hinzufügen:
HF_TOKEN=hf_xxxxxxxxxxxxx
```

Token erstellen: https://huggingface.co/settings/tokens

---

### Problem: Encoding-Fehler (CP1252)
**Symptom:** Sonderzeichen werden falsch dargestellt

**Auswirkung:** Nur kosmetisch (Terminal-Ausgabe)

**Lösung 1:** UTF-8 Terminal verwenden
```bash
chcp 65001  # Windows CMD
```

**Lösung 2:** Ausgabe in Datei umleiten
```bash
python batch_test.py > results.txt 2>&1
```

---

### Problem: "ANTHROPIC_API_KEY not found"
**Symptom:** Fehler beim Initialisieren des Analyzers

**Lösung:** `.env` Datei erstellen
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

API Key erstellen: https://console.anthropic.com/

---

### Problem: Rate Limiting (429 Error)
**Symptom:** Claude API gibt "Too Many Requests" zurück

**Lösung:**
- Pause zwischen Requests einbauen
- API-Tier upgraden (falls nötig)
- Batch-Test in kleineren Gruppen ausführen

---

## 📈 Performance-Benchmarks

### Erwartete Zeiten (CPU: Intel i5/i7, keine GPU)

| Komponente | Erwartete Dauer |
|------------|-----------------|
| Embedding-Modell laden (1x) | 1-3 Sekunden |
| Embedding generieren | 50-200ms |
| Claude API Call | 3-8 Sekunden |
| DB-Speicherung | <10ms |
| **Gesamt pro Dokument** | **4-10 Sekunden** |

**Hinweis:** Erste Ausführung ist langsamer (Modell-Download von HuggingFace)

---

## ✅ Checkliste vor Produktiveinsatz

- [ ] Batch-Test erfolgreich durchgeführt (Success Rate ≥ 85%)
- [ ] Duplikatserkennung funktioniert
- [ ] Eigene Test-Dokumente verarbeitet
- [ ] Performance akzeptabel für Use-Case
- [ ] `.env` konfiguriert (API Key, optional HF Token)
- [ ] Logs überprüft (`archaeologist.log`, `batch_test.log`)
- [ ] Datenbank-Inhalte verifiziert (mit SQLite-Viewer oder `main.py`)
- [ ] README.md gelesen und verstanden

---

## 🎓 Nächste Schritte

Nach erfolgreichem Test:

1. **Produktiv-Daten verarbeiten**
   ```bash
   python main.py /pfad/zu/echten/dokumenten/datei.txt
   ```

2. **Batch-Processing für mehrere Dateien**
   - Skript erweitern oder Loop verwenden:
   ```bash
   for file in /pfad/zu/dokumenten/*.txt; do
       python main.py "$file"
   done
   ```

3. **Features erweitern** (siehe `STATUS.md` → Roadmap)
   - PDF-Support
   - Semantische Suche
   - Web-UI

---

## 📞 Support

Bei unerwarteten Fehlern:
1. Check `batch_test.log` für Details
2. Check `archaeologist.log` für Pipeline-Logs
3. Prüfe `batch_test_results.json` für strukturierte Fehlerinfos
4. GitHub Issue erstellen mit Log-Auszügen

---

**Happy Testing! 🚀**
