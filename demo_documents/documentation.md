# Never-tired-archaeologist - Technical Documentation

**Version:** 3.0.0
**Last Updated:** December 2025
**Author:** Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Integration](#api-integration)
5. [Database Schema](#database-schema)
6. [Search Functionality](#search-functionality)
7. [Best Practices](#best-practices)

---

## Overview

Never-tired-archaeologist is an intelligent document analysis system that leverages modern Large Language Models (LLMs) to extract semantic metadata from unstructured documents. The system combines the power of Claude AI for analysis and Gemini for vector embeddings to provide comprehensive document understanding.

### Key Features

- **Multi-format Support**: Processes PDF, Markdown, Text, Python, JSON, CSV, and HTML files
- **Intelligent Analysis**: Automatic language detection, topic classification, and keyword extraction
- **Duplicate Detection**: Cosine similarity-based duplicate identification
- **Full-text Search**: SQLite FTS5 for blazing-fast document retrieval
- **Persistent Storage**: All analysis results stored in local SQLite database

### Use Cases

1. **Research Management**: Organize and search through academic papers and articles
2. **Code Documentation**: Analyze and categorize code repositories
3. **Knowledge Base**: Build searchable documentation libraries
4. **Content Analysis**: Extract insights from large document collections

---

## Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│              User Interface (GUI)               │
│                  main.py                        │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
┌────────▼────────┐ ┌─────▼──────────┐
│  File Scanner   │ │   Database     │
│ file_scanner.py │ │  database.py   │
└────────┬────────┘ └─────▲──────────┘
         │                │
┌────────▼────────────────┴──────────┐
│      Text Extractor                │
│     text_extractor.py              │
└────────┬───────────────────────────┘
         │
┌────────▼───────────────────────────┐
│     LLM Providers                  │
│   llm_providers.py                 │
│  ┌─────────┐    ┌──────────┐      │
│  │ Claude  │    │  Gemini  │      │
│  │ Haiku   │    │ Embed    │      │
│  └─────────┘    └──────────┘      │
└────────┬───────────────────────────┘
         │
┌────────▼───────────────────────────┐
│    Duplicate Detection             │
│      dupdetect.py                  │
└────────────────────────────────────┘
```

### Technology Stack

- **Language**: Python 3.12+
- **GUI Framework**: Tkinter (built-in)
- **Database**: SQLite with FTS5
- **AI/ML**:
  - Anthropic Claude (Haiku 4.5) for analysis
  - Google Gemini (embedding-001) for vectorization
- **Testing**: pytest with 214 unit tests

---

## Core Components

### 1. File Scanner (`file_scanner.py`)

Recursively scans directories for supported file types.

**Features:**
- Filters by extension (`.txt`, `.md`, `.pdf`, `.py`, `.json`, `.csv`, `.html`)
- Skips hidden files and `_processed` directories
- Returns Path objects for easy handling

**Example:**
```python
from file_scanner import iter_supported_files

for file_path in iter_supported_files(base_dir):
    print(f"Found: {file_path}")
```

### 2. Text Extractor (`text_extractor.py`)

Extracts text content from various file formats.

**Supported Formats:**
- Plain text: `.txt`, `.md`, `.py`, `.json`, `.csv`, `.html`
- PDF: Using PyMuPDF (fitz) library
- Fallback: UTF-8 encoding with error handling

**Example:**
```python
from text_extractor import extract_text

text = extract_text(Path("document.pdf"))
print(f"Extracted {len(text)} characters")
```

### 3. LLM Providers (`llm_providers.py`)

Multi-provider architecture for AI analysis and embeddings.

**Components:**
- `ClaudeProvider`: Metadata extraction using Claude Haiku 4.5
- `GeminiProvider`: Vector embeddings using gemini-embedding-001
- `MultiProvider`: Orchestrates both providers

**Metadata Extraction:**
```python
{
    "language": "en",           # ISO 639-1 code
    "topic": "Machine Learning",
    "keywords": ["AI", "neural networks", "training"],
    "summary": "A comprehensive guide to...",
    "is_prompt": false,
    "is_llm_output": false,
    "git_project": "tensorflow",
    "confidence": 0.95
}
```

### 4. Database (`database.py`)

Persistent storage with SQLite and FTS5 full-text search.

**Schema:**
- `documents`: Core document information
- `metadata`: Extracted metadata (language, topic, keywords)
- `embeddings`: Vector embeddings (768 dimensions)
- `duplicates`: Duplicate relationships
- `documents_fts`: FTS5 search index

**Example:**
```python
from database import Database

db = Database(Path("archaeologist.db"))
doc_id = db.insert_document(
    filename="example.txt",
    filepath="/path/to/example.txt",
    original_text=text,
    metadata=extracted_metadata,
    embedding=vector
)
```

### 5. Duplicate Detection (`dupdetect.py`)

Finds similar documents using cosine similarity.

**Algorithm:**
```python
similarity = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
```

**Threshold:** 0.95 (configurable in `main.py`)

---

## API Integration

### Claude API (Anthropic)

**Model:** claude-haiku-4.5
**Endpoint:** Anthropic REST API
**Rate Limits:** 50 RPM (Tier 1)

**Configuration:**
```python
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Pricing:**
- Input: $1.00 per 1M tokens
- Output: $5.00 per 1M tokens
- With prompt caching: ~90% savings

### Gemini API (Google)

**Model:** gemini-embedding-001
**Dimensions:** 768 (default)
**Rate Limits:** 15 RPM (Free tier)

**Configuration:**
```python
GOOGLE_API_KEY=AIza-your-key-here
```

**Pricing:**
- Embeddings: $0.00 (Free tier, 1.5M tokens/day)
- Paid tier: $0.10 per 1M tokens

---

## Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT UNIQUE NOT NULL,
    source_extension TEXT NOT NULL,
    source_type TEXT NOT NULL,
    original_text TEXT NOT NULL,
    wordcount INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    processed_at TEXT NOT NULL
);
```

### Metadata Table
```sql
CREATE TABLE metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    language TEXT,
    topic TEXT,
    keywords TEXT,  -- JSON array
    summary TEXT,
    is_prompt INTEGER DEFAULT 0,
    is_llm_output INTEGER DEFAULT 0,
    git_project TEXT,
    confidence REAL,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

### FTS5 Virtual Table
```sql
CREATE VIRTUAL TABLE documents_fts USING fts5(
    filename,
    original_text,
    content=documents,
    content_rowid=id
);
```

---

## Search Functionality

### Full-Text Search (FTS5)

The system uses SQLite's FTS5 extension for powerful full-text search capabilities.

**Basic Search:**
```sql
SELECT * FROM documents_fts WHERE documents_fts MATCH 'python';
```

**Boolean Operators:**
```sql
-- AND operator
'python AND tutorial'

-- OR operator
'javascript OR typescript'

-- NOT operator
'python NOT tutorial'

-- Phrase search
'"machine learning"'
```

**Advanced Features:**
- Ranking by relevance (BM25 algorithm)
- Prefix matching: `"pyth*"`
- Column-specific search: `filename:test`

### GUI Search

The GUI provides a user-friendly search interface:

1. Enter query in search field
2. Press Enter or click 🔍 button
3. Results displayed with:
   - Filename
   - File path
   - Language
   - Topic
   - Keywords (top 5)
   - Summary (truncated to 150 chars)
   - Word count

---

## Best Practices

### 1. Performance Optimization

**Batch Processing:**
- Process documents in batches of 100
- Use prompt caching to reduce costs
- Monitor API rate limits

**Database:**
- Regular VACUUM to optimize database
- Index frequently queried columns
- Use prepared statements

### 2. Error Handling

**Graceful Degradation:**
- Continue processing on single-file errors
- Log errors to `error_log.txt`
- Display user-friendly error messages

**API Resilience:**
- Implement exponential backoff for rate limits
- Fallback to local embeddings if cloud fails
- Cache successful responses

### 3. Security

**API Keys:**
- Never commit `.env` to version control
- Use environment variables
- Rotate keys regularly

**Data Privacy:**
- All processing happens locally
- No data sent to third parties except APIs
- SQLite database stays on local machine

### 4. Testing

**Test Coverage:**
- 214 unit tests across all modules
- Mock external APIs for fast testing
- Integration tests for critical paths

**Run Tests:**
```bash
pytest tests/ -v --cov=.
```

---

## Performance Metrics

### Typical Processing Time

| Document Type | Size | Processing Time |
|---------------|------|-----------------|
| Plain Text    | 10KB | ~1 second       |
| Markdown      | 50KB | ~2 seconds      |
| PDF           | 1MB  | ~5 seconds      |
| Python Code   | 20KB | ~1.5 seconds    |

### Scalability

- **1000 documents**: ~30 minutes (with API limits)
- **Database size**: ~3KB per document (with embeddings)
- **Search performance**: <100ms for most queries

---

## Troubleshooting

### Common Issues

**1. API Key Errors**
```
ERROR: ANTHROPIC_API_KEY not found
```
**Solution:** Create `.env` file with API keys

**2. PDF Extraction Fails**
```
ERROR: PyMuPDF not installed
```
**Solution:** `pip install PyMuPDF`

**3. Database Locked**
```
ERROR: database is locked
```
**Solution:** Close other instances accessing the DB

**4. Rate Limit Exceeded**
```
ERROR: Rate limit exceeded (429)
```
**Solution:** Wait 60 seconds or use exponential backoff

---

## Roadmap

### Planned Features

- [ ] Cloud storage integration (S3, Google Drive)
- [ ] Multi-language UI
- [ ] Export to various formats (CSV, Excel)
- [ ] Advanced filtering options
- [ ] Custom metadata fields
- [ ] Collaborative features

### Future Enhancements

- Local LLM support (Ollama, LLaMA)
- GPU acceleration for embeddings
- Web interface (FastAPI + React)
- Real-time document watching
- OCR for scanned documents

---

## Contributing

This is currently a personal project, but contributions are welcome!

**Development Setup:**
1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Submit pull request

**Code Style:**
- Follow PEP 8
- Use type hints
- Document all functions
- Write comprehensive tests

---

## License

MIT License - See LICENSE file for details

---

## Contact

- **GitHub**: https://github.com/Imperativ/Never-tired-archaeologist
- **Documentation**: See README.md
- **Issues**: GitHub Issues

---

**Last Updated:** December 6, 2025
**Version:** 3.0.0
**Python:** 3.12+
