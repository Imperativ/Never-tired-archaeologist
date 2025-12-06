<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# fang an

Basierend auf meiner Live-Recherche erstelle ich jetzt den vollständigen Bericht gemäß deinem Template:

***

# LLM API Recherche für Dokumentenanalyse-Tool

## A) Validierung (PFLICHT)

**Recherche-Datum:** Freitag, 5. Dezember 2025, 02:38 CET

**Quellen verwendet:**

- Offizielle Anthropic Claude Dokumentation (platform.claude.com)[^1][^2][^3][^4]
- Google Gemini API Dokumentation (ai.google.dev)[^5][^6][^7][^8]
- Perplexity API Dokumentation (docs.perplexity.ai)[^9][^10][^11]
- Sentence Transformers Dokumentation (sbert.net)[^12]
- Diverse Fachpublikationen und Benchmark-Studien (2024-2025)[^13][^14][^15][^16][^17]

**Aktuelle Modellversionen (Stand Dezember 2025):**

### Anthropic Claude

- **Claude Opus 4** (Released: 22. Mai 2025)[^18]
- **Claude Sonnet 4.5** (Released: Oktober 2025)[^19][^2]
- **Claude Haiku 4.5** (Released: 13. Oktober 2025)[^19]
- **Claude Haiku 3.5** (Verfügbar)
- **WICHTIG:** Claude Sonnet 3.5 ist VERALTET – aktuelle Version ist Sonnet 4.5[^20][^21]


### Google Gemini

- **Gemini 2.0 Flash** (Released: 11. Dezember 2024)[^6][^5]
- **Gemini 2.5 Pro** (Experimentell verfügbar)[^22][^23]
- **Gemini 2.5 Flash-Lite** (Verfügbar)[^23]
- **Embedding-Modell:** `text-embedding-004` (Released: 9. April 2024) sowie neues experimentelles Modell `gemini-embedding-exp-03-07` (Released: 7. März 2025)[^24][^6]


### Perplexity

- **Sonar** (basiert auf Llama 3.3 70B)[^25]
- **Sonar Pro** (Released: Januar 2025)[^26][^27]
- **Sonar Reasoning Pro** (basiert auf DeepSeek-R1)[^25]
- **WICHTIG:** Perplexity hat mehrere Modelle aus der API entfernt (z.B. Llama-instruct Ende 2024)[^28]

***

## B) Kostenvergleich-Tabelle

Für **1000 Dokumente à ~2000 Tokens Input** (= 2M Tokens Input) mit geschätzten 500 Tokens Output pro Dokument (= 0,5M Tokens Output):


| Strategie | Analyse-Modell | Embedding-Modell | Kosten Analyse | Kosten Embeddings | Gesamt | Rate Limits (API) |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **Claude Sonnet 4.5 + Gemini Embed** | Claude Sonnet 4.5 | text-embedding-004 | \$6 + \$7.50 = **\$13.50** | \$0 (Free Tier) oder \$0.20 (Paid) | **\$13.50-\$13.70** | 50 RPM (Tier 1)[^4][^29] |
| **Claude Opus 4 + Gemini Embed** | Claude Opus 4 | text-embedding-004 | \$30 + \$37.50 = **\$67.50** | \$0 (Free) oder \$0.20 (Paid) | **\$67.50-\$67.70** | 50 RPM (Tier 1)[^4] |
| **Claude Haiku 4.5 + Gemini Embed** | Claude Haiku 4.5 | text-embedding-004 | \$2 + \$2.50 = **\$4.50** | \$0 (Free) oder \$0.20 (Paid) | **\$4.50-\$4.70** | 50 RPM (Tier 1)[^4] |
| **Nur Gemini 2.0 Flash** | Gemini 2.0 Flash | text-embedding-004 | \$0.60 + \$1.25 = **\$1.85** | \$0 (Free) oder \$0.20 (Paid) | **\$1.85-\$2.05** | 15 RPM (Free)[^23][^30] |
| **Nur Gemini 2.5 Pro** | Gemini 2.5 Pro | text-embedding-004 | \$2.50 + \$5.00 = **\$7.50** | \$0 (Free) oder \$0.20 (Paid) | **\$7.50-\$7.70** | 5 RPM (Free)[^23][^30] |
| **Claude Sonnet 4.5 + Lokale Embeddings** | Claude Sonnet 4.5 | sentence-transformers (lokal) | \$6 + \$7.50 = **\$13.50** | \$0 (lokal) | **\$13.50** | 50 RPM (Tier 1)[^4] |
| **Perplexity Sonar + Gemini Embed** | Sonar | text-embedding-004 | \$2 + \$0.50 = **\$2.50** | \$0 (Free) oder \$0.20 (Paid) | **\$2.50-\$2.70** | Variabel (API)[^9] |
| **Perplexity Sonar Pro + Gemini Embed** | Sonar Pro | text-embedding-004 | \$6 + \$7.50 = **\$13.50** | \$0 (Free) oder \$0.20 (Paid) | **\$13.50-\$13.70** | Variabel (API)[^9] |

**Hinweise zur Tabelle:**

- Preise basieren auf offiziellen API-Dokumentationen (Dezember 2024/2025)[^2][^7][^9]
- Gemini Free Tier: 1,5M Tokens/Tag (= ausreichend für 750 Dokumente/Tag bei 2k Tokens Input)[^7][^8][^23]
- Claude Batch API: 50% Rabatt verfügbar (z.B. Sonnet 4.5: \$1.50 Input / \$7.50 Output pro 1M Tokens)[^31][^2]
- Rate Limits variieren je nach Usage Tier (Claude) bzw. Paid/Free (Gemini)

***

## C) Konkrete Empfehlung

Basierend auf deinen Constraints (vorhandene Claude Pro/API + Gemini Pro/API + Perplexity Pro, **kein OpenAI**, moderate Kosten, Dell Laptop ohne GPU, Python 3.13):

### 1. **Primäre Empfehlung: Claude Haiku 4.5 + Gemini Free Tier Embeddings**

**Begründung:**

- **Analyse mit Claude Haiku 4.5** (\$4.50 per 1000 Dokumente)[^31]
    - Schnellstes Claude-Modell (< 1 Sekunde Response)[^21]
    - Ausreichend für Metadaten-Extraktion (Sprache, Topic, Keywords, Summary)
    - **Structured Output** via Tool Use verfügbar[^32][^33][^34]
    - 50 Requests/Minute (Tier 1), skalierbar[^4][^29]
- **Embeddings mit Gemini `text-embedding-004`** (Free Tier)[^7]
    - 768 Dimensionen (optimal für Duplikaterkennung)[^35][^36]
    - Kostenlos bis 1,5M Tokens/Tag = 750 Dokumente/Tag[^8][^7]
    - 15 RPM im Free Tier, ausreichend für Batch-Verarbeitung[^8][^23]
    - Bei Überschreitung: \$0.10 per 1M Input Tokens (Paid)[^7]

**Kostenabschätzung pro 1000 Dokumente:** \$4.50 - \$4.70

**Vorteil:** Beste Balance aus Geschwindigkeit, Kosten und Qualität. Haiku 4.5 ist 5-10x schneller als Sonnet bei akzeptabler Qualität für strukturierte Extraktion.[^21][^19]

***

### 2. **Fallback: Gemini 2.0 Flash + lokale Embeddings**

**Begründung:**

- **Analyse mit Gemini 2.0 Flash** (\$1.85 per 1000 Dokumente)[^7]
    - Günstiger als Claude Haiku 4.5
    - Sehr schnell (2x schneller als Gemini 1.5 Pro)[^37][^5]
    - **JSON Mode verfügbar** für strukturierte Ausgabe[^38][^6]
    - 15 RPM im Free Tier[^23][^8]
- **Embeddings lokal mit `sentence-transformers/all-MiniLM-L6-v2`** (kostenlos)[^39][^12]
    - 384 Dimensionen, schnell auf CPU (18.000 Queries/Sekunde GPU, 750/Sekunde CPU)[^12]
    - 22M Parameter, ~90 MB Modellgröße[^39]
    - Gut geeignet für Dell Laptop ohne GPU[^40]

**Kostenabschätzung pro 1000 Dokumente:** \$1.85 (Analyse) + \$0 (Embeddings) = **\$1.85**

**Vorteil:** Niedrigste Kosten, vollständig unabhängig von Cloud-Embeddings. Nachteil: Leicht geringere Embedding-Qualität vs. `text-embedding-004`.[^41]

***

### 3. **Embedding-Strategie: Cloud (Gemini) bevorzugt, Lokal als Backup**

**Empfehlung:**

1. **Primär:** Gemini `text-embedding-004` (768d) im Free Tier[^36][^7]
    - Solange < 750 Dokumente/Tag → kostenlos
    - Bei höherem Volumen: Paid Tier (\$0.10 per 1M Tokens = \$0.20 per 1000 Dokumente)[^7]
2. **Backup:** Lokale `sentence-transformers/all-mpnet-base-v2` (768d)[^42][^12]
    - Falls Gemini Rate Limits erreicht oder Offline-Fähigkeit gewünscht
    - Höhere Qualität als MiniLM, aber langsamer (4.000 Queries/Sekunde GPU, 170/Sekunde CPU)[^12]
    - ~420 MB Modellgröße[^43]

**Hybrid-Ansatz:**

- Tag 1-750: Gemini Free Tier
- Ab 751+: Wechsel zu lokalen Embeddings oder Paid Tier (je nach Budget)

***

## D) Code-Snippets (Aktuelle SDK-Versionen)

### 1. Claude API - Strukturierter JSON-Output mit Haiku 4.5

**SDK Version:** `anthropic` (neueste: 0.x, Stand Dezember 2024)[^44]

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Definiere dein JSON-Schema als Tool
tools = [
    {
        "name": "extract_metadata",
        "description": "Extrahiert Metadaten aus einem Dokument",
        "input_schema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Erkannte Sprache (ISO 639-1 Code, z.B. 'de', 'en')"
                },
                "topic": {
                    "type": "string",
                    "description": "Hauptthema des Dokuments"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Liste von 5-10 Keywords"
                },
                "summary": {
                    "type": "string",
                    "description": "Zusammenfassung in 2-3 Sätzen"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["systemprompt", "llm_output", "code", "documentation", "other"],
                    "description": "Klassifikation des Content-Typs"
                },
                "project": {
                    "type": "string",
                    "description": "Zuordnung zu bekanntem Projekt (oder 'unknown')"
                }
            },
            "required": ["language", "topic", "keywords", "summary", "content_type", "project"]
        }
    }
]

# Dokument analysieren
document_text = """
Dein Dokumententext hier...
"""

message = client.messages.create(
    model="claude-haiku-4-5-20251022",  # Aktuelles Modell-ID
    max_tokens=2048,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": f"Analysiere folgendes Dokument und extrahiere die Metadaten:\n\n{document_text}"
        }
    ]
)

# Extrahiere strukturierte Daten
for block in message.content:
    if block.type == "tool_use" and block.name == "extract_metadata":
        metadata = block.input
        print(f"Language: {metadata['language']}")
        print(f"Topic: {metadata['topic']}")
        print(f"Keywords: {', '.join(metadata['keywords'])}")
        print(f"Summary: {metadata['summary']}")
        print(f"Content Type: {metadata['content_type']}")
        print(f"Project: {metadata['project']}")
```

**Alternative: Structured Output mit JSON Mode (Beta, verfügbar seit Nov. 2024):**[^34][^32]

```python
# Noch in Beta, aber offiziell angekündigt für Sonnet 4.5 und Opus 4.1
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2048,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "type": "object",
            "properties": {
                "language": {"type": "string"},
                "topic": {"type": "string"},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
                "content_type": {"type": "string"},
                "project": {"type": "string"}
            },
            "required": ["language", "topic", "keywords", "summary"]
        }
    },
    messages=[
        {"role": "user", "content": f"Extract metadata from this document: {document_text}"}
    ]
)
```


***

### 2. Gemini Embedding-Generierung (text-embedding-004)

**SDK Version:** `google-generativeai` (neueste: 0.x, Stand Dezember 2024)[^6]

```python
import os
import google.generativeai as genai

# Konfiguration
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Embedding-Modell
embedding_model = "models/text-embedding-004"

# Einzelnes Dokument embedden
def embed_single_document(text: str, task_type: str = "retrieval_document") -> list[float]:
    """
    Erzeugt Embedding für ein Dokument.
    
    Args:
        text: Dokumententext (max. 8.000 Tokens bei text-embedding-004)
        task_type: "retrieval_document" (für Datenbank) oder "retrieval_query" (für Suche)
    
    Returns:
        768-dimensionaler Vektor (Standard)
    """
    result = genai.embed_content(
        model=embedding_model,
        content=text,
        task_type=task_type,
        output_dimensionality=768  # Optional: 128-768 (MRL-Support)
    )
    return result['embedding']

# Batch-Embeddings (max. 100 Dokumente pro Request)
def embed_batch_documents(texts: list[str]) -> list[list[float]]:
    """
    Erzeugt Embeddings für mehrere Dokumente.
    Gemini erlaubt max. 100 Dokumente pro Batch-Request.
    """
    embeddings = []
    batch_size = 100
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        result = genai.embed_content(
            model=embedding_model,
            content=batch,
            task_type="retrieval_document",
            output_dimensionality=768
        )
        embeddings.extend(result['embedding'])
    
    return embeddings

# Beispiel: 1000 Dokumente embedden
documents = ["Text 1", "Text 2", ...]  # Deine 1000 Dokumente
all_embeddings = embed_batch_documents(documents)

print(f"Erzeugt {len(all_embeddings)} Embeddings à {len(all_embeddings[^0])} Dimensionen")
```

**WICHTIG:** Gemini Free Tier Rate Limits beachten:[^30][^8][^23]

- 15 Requests/Minute
- 1,5M Tokens/Tag (entspricht ~750 Dokumente à 2k Tokens)

**Rate Limiting Wrapper:**

```python
import time
from datetime import datetime, timedelta

class GeminiRateLimiter:
    def __init__(self, rpm=15, tpd=1_500_000):
        self.rpm = rpm
        self.tpd = tpd
        self.requests_this_minute = 0
        self.tokens_today = 0
        self.minute_start = datetime.now()
        self.day_start = datetime.now()
    
    def wait_if_needed(self, estimated_tokens: int):
        now = datetime.now()
        
        # Reset Minute Counter
        if (now - self.minute_start) > timedelta(minutes=1):
            self.requests_this_minute = 0
            self.minute_start = now
        
        # Reset Day Counter
        if (now - self.day_start) > timedelta(days=1):
            self.tokens_today = 0
            self.day_start = now
        
        # Check Limits
        if self.requests_this_minute >= self.rpm:
            sleep_time = 60 - (now - self.minute_start).seconds
            print(f"RPM Limit erreicht. Warte {sleep_time}s...")
            time.sleep(sleep_time)
            self.requests_this_minute = 0
            self.minute_start = datetime.now()
        
        if self.tokens_today + estimated_tokens > self.tpd:
            print(f"Daily Token Limit erreicht. Wechsel zu lokalem Embedding oder Paid Tier.")
            raise Exception("Gemini Daily Limit exceeded")
        
        self.requests_this_minute += 1
        self.tokens_today += estimated_tokens

# Verwendung:
limiter = GeminiRateLimiter()

for doc in documents:
    limiter.wait_if_needed(estimated_tokens=2000)  # Deine avg. Doc-Größe
    embedding = embed_single_document(doc)
    # Speichere embedding in DB...
```


***

### 3. Perplexity API (Sonar für Dokumentenanalyse)

**HINWEIS:** Perplexity API ist primär für **Web-Search-grounded Queries** optimiert. Für reine Textanalyse ohne Web-Search ist Claude oder Gemini besser geeignet. Perplexity Sonar ist daher **nicht empfohlen** für dein Use-Case (Metadaten-Extraktion aus lokalen Dokumenten).[^11][^27][^26]

Falls du dennoch testen möchtest:

```python
import os
import requests

# Perplexity API
api_key = os.environ.get("PERPLEXITY_API_KEY")
url = "https://api.perplexity.ai/chat/completions"

def analyze_with_perplexity(document_text: str) -> dict:
    """
    Analysiert Dokument mit Perplexity Sonar.
    NICHT empfohlen für lokale Dokumente ohne Web-Search-Bedarf.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",  # oder "sonar-pro" für höhere Qualität
        "messages": [
            {
                "role": "system",
                "content": "Extract metadata from the following document in JSON format."
            },
            {
                "role": "user",
                "content": document_text
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Test (NICHT für Produktion empfohlen)
# result = analyze_with_perplexity("Your document text...")
# print(result)
```

**Perplexity API Preise (Stand Januar 2025):**[^27][^9][^11]

- **Sonar:** \$1 per 1M Input/Output Tokens + \$5 per 1.000 Searches
- **Sonar Pro:** \$3 per 1M Input, \$15 per 1M Output + \$5 per 1.000 Searches

**Fazit:** Für dein Dokumentenanalyse-Tool sind Claude Haiku 4.5 oder Gemini 2.0 Flash deutlich besser geeignet und günstiger.

***

### 4. Lokale Embeddings mit sentence-transformers (Backup-Lösung)

**Bibliothek:** `sentence-transformers` (neueste Version via pip)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Modell laden (wird beim ersten Mal heruntergeladen, danach gecacht)
# Empfehlung: all-mpnet-base-v2 (768d, beste Qualität) oder all-MiniLM-L6-v2 (384d, schneller)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Alternativ für schnellere Performance auf CPU:
# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_documents_local(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """
    Erzeugt Embeddings lokal auf CPU.
    
    Args:
        texts: Liste von Dokumententexten
        batch_size: Batch-Größe für effizientere Verarbeitung
    
    Returns:
        NumPy-Array mit Embeddings (shape: [n_docs, 768] bei mpnet-base-v2)
    """
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings

# Cosine-Similarity für Duplikaterkennung
from sentence_transformers.util import cos_sim

def find_duplicates(embeddings: np.ndarray, threshold: float = 0.95) -> list[tuple[int, int, float]]:
    """
    Findet potenzielle Duplikate via Cosine-Similarity.
    
    Args:
        embeddings: Embedding-Matrix
        threshold: Similarity-Schwellwert (0.95 = 95% ähnlich)
    
    Returns:
        Liste von (doc_idx1, doc_idx2, similarity_score)
    """
    similarities = cos_sim(embeddings, embeddings)
    duplicates = []
    
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            if similarities[i][j] >= threshold:
                duplicates.append((i, j, float(similarities[i][j])))
    
    return duplicates

# Beispiel: 1000 Dokumente lokal embedden
documents = ["Text 1", "Text 2", ...]  # Deine Dokumente
embeddings = embed_documents_local(documents)

# Duplikate finden
duplicates = find_duplicates(embeddings, threshold=0.95)
print(f"Gefunden: {len(duplicates)} potenzielle Duplikate")
```

**Performance auf Dell Laptop (CPU-only):**[^45][^43][^12]

- **all-mpnet-base-v2:** ~170 Queries/Sekunde (CPU), 768 Dimensionen
- **all-MiniLM-L6-v2:** ~750 Queries/Sekunde (CPU), 384 Dimensionen
- 1000 Dokumente embedden: ~6-30 Sekunden (je nach Modell und CPU)

**Empfehlung:** Für 1000 Dokumente ist lokale Verarbeitung absolut praktikabel. Bei > 10.000 Dokumenten solltest du Gemini Paid Tier in Betracht ziehen.

***

## Zusammenfassung \& Best Practice

### Empfohlener Tech-Stack:

```
┌─────────────────────────────────────────────┐
│  Python 3.13 Dokumentenanalyse-Tool         │
├─────────────────────────────────────────────┤
│                                             │
│  METADATEN-EXTRAKTION:                      │
│  ✓ Claude Haiku 4.5                         │
│    - Structured Output via Tool Use         │
│    - $4.50 per 1000 Dokumente               │
│    - 50 RPM (Tier 1)                        │
│                                             │
│  EMBEDDING-GENERIERUNG:                     │
│  ✓ Gemini text-embedding-004 (Free Tier)    │
│    - 768 Dimensionen                        │
│    - Kostenlos bis 750 Docs/Tag             │
│    - 15 RPM                                 │
│                                             │
│  BACKUP (bei Rate Limit):                   │
│  ✓ sentence-transformers/all-mpnet-base-v2  │
│    - Lokal auf CPU                          │
│    - $0 Kosten                              │
│                                             │
│  SPEICHERUNG:                               │
│  ✓ SQLite FTS5 (Volltextsuche)              │
│  ✓ Vector-DB für Embeddings (z.B. Chroma)   │
│                                             │
└─────────────────────────────────────────────┘
```


### Workflow:

1. **Dokument einlesen** → Python 3.13
2. **Metadaten extrahieren** → Claude Haiku 4.5 API (strukturierter JSON-Output)
3. **Embedding generieren** → Gemini `text-embedding-004` (primär) oder lokale sentence-transformers (Backup)
4. **Duplikate erkennen** → Cosine-Similarity auf Embeddings
5. **Speichern** → SQLite (Metadaten + FTS5) + Vector-DB (Embeddings)

### Kostenabschätzung (1000 Dokumente):

- **Claude Haiku 4.5:** \$4.50
- **Gemini Embeddings (Free Tier):** \$0
- **Gesamt:** **\$4.50**

Bei Skalierung auf 10.000 Dokumente/Monat:

- Claude: \$45
- Gemini Embeddings: \$2 (falls Paid Tier nötig)
- **Gesamt: ~\$47/Monat**

Das liegt deutlich unter Enterprise-Budgets und ist mit deinen vorhandenen Abos (Claude Pro/API + Gemini Pro/API) optimal nutzbar.

***

**Quellen:**
<span style="display:none">[^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^110][^111][^112][^113][^114][^115][^116][^117][^118][^119][^120][^121][^122][^123][^124][^125][^126][^127][^128][^129][^130][^131][^132][^133][^134][^135][^136][^137][^138][^139][^140][^141][^142][^143][^144][^145][^146][^147][^148][^149][^150][^151][^152][^153][^154][^155][^156][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div align="center">⁂</div>

[^1]: https://platform.claude.com/docs/en/release-notes/overview

[^2]: https://platform.claude.com/docs/en/about-claude/pricing

[^3]: https://platform.claude.com/docs/en/about-claude/models/overview

[^4]: https://platform.claude.com/docs/en/api/rate-limits

[^5]: https://blog.google/technology/google-deepmind/google-gemini-ai-update-december-2024/

[^6]: https://ai.google.dev/gemini-api/docs/changelog

[^7]: https://ai.google.dev/gemini-api/docs/pricing

[^8]: https://ai.google.dev/gemini-api/docs/rate-limits

[^9]: https://docs.perplexity.ai/getting-started/pricing

[^10]: https://docs.perplexity.ai/getting-started/models/models/sonar-reasoning-pro

[^11]: https://www.perplexity.ai/hub/blog/new-sonar-search-modes-outperform-openai-in-cost-and-performance

[^12]: https://www.sbert.net/docs/sentence_transformer/pretrained_models.html

[^13]: https://jamanetwork.com/journals/jamaophthalmology/fullarticle/2841079

[^14]: https://www.nature.com/articles/s41598-025-18306-1

[^15]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11792186/

[^16]: https://ieeexplore.ieee.org/document/11007529/

[^17]: https://academic.oup.com/jes/article/doi/10.1210/jendso/bvaf149.1312/8299730

[^18]: https://intuitionlabs.ai/articles/anthropic-claude-4-llm-evolution

[^19]: https://www.anthropic.com/news/claude-haiku-4-5

[^20]: https://www.datastudios.org/post/all-claude-ai-models-available-in-2025-full-list-for-web-app-api-and-cloud-platforms

[^21]: https://www.datastudios.org/post/claude-opus-4-vs-sonnet-4-vs-haiku-3-5-functionalities-performance-and-practical-differences-betwe

[^22]: https://blog.laozhang.ai/api-guides/gemini-2-5-pro-api-free/

[^23]: https://blog.laozhang.ai/api-guides/gemini-api-free-tier/

[^24]: https://simonwillison.net/2025/Mar/7/gemini-embeddings/

[^25]: https://www.datastudios.org/post/perplexity-ai-all-models-available-list-categories-usage-etc

[^26]: https://www.perplexity.ai/de/hub/blog/introducing-the-sonar-pro-api

[^27]: https://americanbazaaronline.com/2025/01/22/perplexity-launches-sonar-api-for-ai-search458623/

[^28]: https://www.reddit.com/r/perplexity_ai/comments/1ha7i1n/perplexity_removed_llama_instruct_sonar_nononline/

[^29]: https://obot.ai/resources/learning-center/claude-api/

[^30]: https://www.cometapi.com/how-to-fix-google-gemini-2-5-pro-api-rate-limits/

[^31]: https://costgoat.com/pricing/claude-api

[^32]: https://www.claude.com/blog/structured-outputs-on-the-claude-developer-platform

[^33]: https://baz.co/resources/how-to-achieve-structured-output-in-claude-3-7-three-practical-approaches

[^34]: https://www.xugj520.cn/en/archives/claude-structured-outputs-api-guide.html

[^35]: https://hexdocs.pm/gemini_ex/embeddings.html

[^36]: https://docs.agno.com/basics/knowledge/embedder/gemini/overview

[^37]: https://developers.googleblog.com/en/the-next-chapter-of-the-gemini-era-for-developers/

[^38]: https://docs.litellm.ai/docs/completion/json_mode

[^39]: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

[^40]: https://systenics.ai/blog/2024-02-26-local-embedding-server-using-python/

[^41]: https://modal.com/blog/mteb-leaderboard-article

[^42]: https://huggingface.co/sentence-transformers/all-mpnet-base-v2

[^43]: https://huggingface.co/sentence-transformers/all-mpnet-base-v2/discussions/43

[^44]: https://github.com/anthropics/anthropic-sdk-python

[^45]: https://milvus.io/ai-quick-reference/what-are-some-popular-pretrained-sentence-transformer-models-and-how-do-they-differ-for-example-allminilml6v2-vs-allmpnetbasev2

[^46]: https://academic.oup.com/jes/article/doi/10.1210/jendso/bvaf149.1794/8299452

[^47]: https://www.jmir.org/2025/1/e73918

[^48]: https://www.semanticscholar.org/paper/250ba3fc9aa16ab359cc456bddff5569eadc5d3a

[^49]: https://www.sciltp.com/journals/tai/articles/2504000291

[^50]: https://www.semanticscholar.org/paper/59bbe382b85ceef85b5480e3dd17002524f85c5d

[^51]: https://aacrjournals.org/cancerres/article/85/8_Supplement_1/6836/760681/Abstract-6836-Analysis-of-81-plasma-cytokine

[^52]: https://aacrjournals.org/clincancerres/article/31/13_Supplement/B021/763253/Abstract-B021-Current-oncological-large-language

[^53]: https://philnauki.mgimo.ru/jour/article/view/624

[^54]: http://arxiv.org/pdf/2404.13813.pdf

[^55]: http://arxiv.org/pdf/2503.18129.pdf

[^56]: https://arxiv.org/pdf/2310.03302.pdf

[^57]: https://arxiv.org/pdf/2503.04378.pdf

[^58]: https://arxiv.org/html/2504.03767v2

[^59]: https://arxiv.org/pdf/2311.16867.pdf

[^60]: https://arxiv.org/html/2410.21514

[^61]: https://www.anthropic.com/transparency

[^62]: https://www.anthropic.com/research/economic-index-geography

[^63]: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html

[^64]: https://www.nops.io/blog/anthropic-api-pricing/

[^65]: https://www.scriptbyai.com/anthropic-claude-timeline/

[^66]: https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration

[^67]: https://aclanthology.org/2023.emnlp-main.614.pdf

[^68]: https://arxiv.org/pdf/2311.12485.pdf

[^69]: https://arxiv.org/pdf/2305.13707.pdf

[^70]: https://docs.warpbuild.com/helios/basics/pricing/model-pricing

[^71]: https://www.cursor-ide.com/blog/claude-sonnet-4-5-pricing

[^72]: https://northflank.com/blog/claude-rate-limits-claude-code-pricing-cost

[^73]: https://www.juheapi.com/blog/claude-pricing-explained-2025-sonnet-opus-haiku-costs

[^74]: https://apidog.com/blog/claude-api-rate-limits/

[^75]: https://journals.lww.com/10.1097/ACM.0000000000006207

[^76]: https://academic.oup.com/ndt/article/doi/10.1093/ndt/gfaf116.1217/8295868

[^77]: https://arxiv.org/abs/2108.04385

[^78]: http://arxiv.org/pdf/2403.05530.pdf

[^79]: https://arxiv.org/pdf/2503.07891.pdf

[^80]: http://arxiv.org/pdf/2312.11805.pdf

[^81]: https://arxiv.org/pdf/2412.18708.pdf

[^82]: https://arxiv.org/pdf/2412.13239.pdf

[^83]: http://arxiv.org/pdf/2410.04199.pdf

[^84]: https://arxiv.org/pdf/2312.11444.pdf

[^85]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions

[^86]: https://blog.google/technology/google-deepmind/gemini-model-updates-february-2025/

[^87]: https://en.wikipedia.org/wiki/Gemini_(language_model)

[^88]: https://arxiv.org/html/2503.07891v1

[^89]: https://ieeexplore.ieee.org/document/11236762/

[^90]: http://arxiv.org/pdf/2404.00311.pdf

[^91]: https://linkinghub.elsevier.com/retrieve/pii/S2666675825000359

[^92]: https://arxiv.org/pdf/2305.05176.pdf

[^93]: https://arxiv.org/pdf/2407.04620.pdf

[^94]: https://arxiv.org/pdf/2308.03558.pdf

[^95]: https://www.glbgpt.com/hub/perplexity-price-in-2025/

[^96]: https://www.withorb.com/blog/perplexity-pricing

[^97]: https://skywork.ai/blog/news/perplexity-pro-vs-max-2025-which-plan-offers-best-value/

[^98]: https://ashvanikumar.com/perplexity-ai-api-pricing-plans-costs-explained-2024/

[^99]: https://apidog.com/blog/perplexity-ai-api/

[^100]: https://ai-sdk.dev/providers/ai-sdk-providers/perplexity

[^101]: https://www.index.dev/blog/perplexity-statistics

[^102]: https://www.apideck.com/blog/how-to-get-your-perplexity-api-key

[^103]: https://dl.acm.org/doi/10.1145/3703323.3703698

[^104]: https://arxiv.org/abs/2407.08008

[^105]: https://www.mdpi.com/2078-2489/15/2/68

[^106]: https://aclanthology.org/2024.semeval-1.260

[^107]: https://www.semanticscholar.org/paper/79d6fa97244e11dee2b4aabbb5c20565bb1e804b

[^108]: https://www.semanticscholar.org/paper/5e3b36a4a1d500afd9329c63faab3fa484228c85

[^109]: https://aclanthology.org/2024.americasnlp-1.19

[^110]: https://aclanthology.org/2024.semeval-1.245

[^111]: https://arxiv.org/abs/2409.05997

[^112]: https://aclanthology.org/2024.semeval-1.65

[^113]: http://arxiv.org/pdf/2411.15242.pdf

[^114]: https://www.aclweb.org/anthology/D18-2029.pdf

[^115]: http://arxiv.org/pdf/2409.15790v1.pdf

[^116]: https://arxiv.org/pdf/2412.13663.pdf

[^117]: https://arxiv.org/pdf/2207.12852.pdf

[^118]: https://aclanthology.org/2023.emnlp-main.821.pdf

[^119]: https://aclanthology.org/2023.nlposs-1.2.pdf

[^120]: https://aclanthology.org/2021.eacl-main.246.pdf

[^121]: https://codesphere.com/articles/best-open-source-sentence-embedding-models

[^122]: https://github.com/MinishLab/model2vec

[^123]: https://dev.to/pringled/model2vec-making-sentence-transformers-500x-faster-on-cpu-and-15x-smaller-4k2b

[^124]: https://www.reddit.com/r/MLQuestions/comments/1gl9kub/cpu_and_gpu_performance_benchmarks_for_e5small/

[^125]: https://docs.langchain.com/oss/python/integrations/text_embedding

[^126]: https://ascopubs.org/doi/10.1200/OP.2025.21.10_suppl.602

[^127]: https://ascopubs.org/doi/10.1200/OP.2025.21.10_suppl.621

[^128]: http://arxiv.org/pdf/2503.01151.pdf

[^129]: http://arxiv.org/pdf/2406.10442.pdf

[^130]: http://arxiv.org/pdf/2310.02953.pdf

[^131]: http://arxiv.org/pdf/2408.11061.pdf

[^132]: https://arxiv.org/pdf/2404.07362.pdf

[^133]: https://arxiv.org/pdf/2407.15021.pdf

[^134]: https://www.reddit.com/r/Anthropic/comments/1hje7fq/structured_json_output/

[^135]: https://www.reddit.com/r/ClaudeAI/comments/1lbalxb/anthropic_released_an_official_python_sdk_for/

[^136]: https://datachain.ai/blog/enforcing-json-outputs-in-commercial-llms

[^137]: https://arxiv.org/pdf/2401.00588.pdf

[^138]: http://arxiv.org/pdf/2411.15997.pdf

[^139]: http://arxiv.org/pdf/2411.09224.pdf

[^140]: https://arxiv.org/pdf/2408.00253.pdf

[^141]: http://arxiv.org/pdf/2312.10637v2.pdf

[^142]: http://arxiv.org/pdf/2401.17644.pdf

[^143]: http://arxiv.org/pdf/2407.13729.pdf

[^144]: http://arxiv.org/pdf/2405.09798.pdf

[^145]: https://www.reddit.com/r/Bard/comments/1n6exsd/why_do_i_only_get_50_free_requests_per_day_for/

[^146]: https://aifreeapi.com/en/posts/gemini-api-key-guide

[^147]: https://support.google.com/gemini/thread/380160476/getting-429-rate-limit-exceeded-on-gemini-api?hl=en

[^148]: https://www.ibbaka.com/ibbaka-market-blog/ai-pricing-studies-cohere-llm

[^149]: https://cohere.com/pricing

[^150]: https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-024-06778-9

[^151]: https://link.springer.com/10.1007/s00405-025-09628-x

[^152]: https://return.publikasikupublisher.com/index.php/return/article/view/348

[^153]: https://malariajournal.biomedcentral.com/articles/10.1186/s12936-025-05668-0

[^154]: https://link.springer.com/10.1007/s12020-025-04294-9

[^155]: https://www.mdpi.com/2075-4418/15/6/672

[^156]: https://dl.acm.org/doi/10.1145/3766918.3766934

