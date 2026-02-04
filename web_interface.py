"""
Web Interface for Never-Tired-Archaeologist
Flask-based document search and browsing interface
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
import hashlib

from flask import Flask, render_template, request, jsonify, send_from_directory
import numpy as np

from src.database import DocDatabase
from src.embedder import LocalEmbedder
from src.models import DocumentMetadata


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Support for UTF-8

# Initialize components
db = DocDatabase()
embedder = None  # Lazy load


def get_embedder():
    """Lazy load embedder (heavy operation)"""
    global embedder
    if embedder is None:
        logger.info("Loading embedding model...")
        embedder = LocalEmbedder()
    return embedder


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of document content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@app.route('/')
def index():
    """Home page with search interface"""
    # Get statistics
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]

    # Get all unique languages and topics
    cursor.execute("SELECT DISTINCT metadata_json FROM documents")
    languages = set()
    topics = set()

    for row in cursor.fetchall():
        metadata = json.loads(row[0])
        if metadata.get('language'):
            languages.add(metadata['language'])
        if metadata.get('topics'):
            topics.update(metadata['topics'])

    stats = {
        'total_documents': total_docs,
        'languages': sorted(languages),
        'topics': sorted(topics)[:50]  # Limit to top 50 topics
    }

    return render_template('index.html', stats=stats)


@app.route('/api/search', methods=['GET'])
def search():
    """Search documents by text query"""
    query = request.args.get('q', '').strip()
    language = request.args.get('lang', '')
    topic = request.args.get('topic', '')
    limit = int(request.args.get('limit', 20))

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    cursor = db.conn.cursor()

    # Build SQL query with filters
    sql = "SELECT id, content, metadata_json, created_at FROM documents WHERE 1=1"
    params = []

    # Full-text search in content
    sql += " AND (content LIKE ? OR metadata_json LIKE ?)"
    search_pattern = f"%{query}%"
    params.extend([search_pattern, search_pattern])

    # Language filter
    if language:
        sql += " AND metadata_json LIKE ?"
        params.append(f'%"language": "{language}"%')

    # Topic filter
    if topic:
        sql += " AND metadata_json LIKE ?"
        params.append(f'%{topic}%')

    sql += f" ORDER BY created_at DESC LIMIT {limit}"

    cursor.execute(sql, params)

    results = []
    for row in cursor.fetchall():
        doc_id, content, metadata_json, created_at = row
        metadata = json.loads(metadata_json)

        # Create snippet (first 200 chars of content)
        snippet = content[:200] + "..." if len(content) > 200 else content

        results.append({
            'id': doc_id,
            'title': metadata.get('title', 'Untitled'),
            'language': metadata.get('language', 'unknown'),
            'topics': metadata.get('topics', []),
            'summary': metadata.get('summary', ''),
            'snippet': snippet,
            'created_at': created_at
        })

    return jsonify({
        'query': query,
        'total_results': len(results),
        'results': results
    })


@app.route('/api/semantic-search', methods=['POST'])
def semantic_search():
    """Find similar documents using embedding similarity"""
    data = request.json
    query_text = data.get('query', '').strip()
    limit = int(data.get('limit', 10))

    if not query_text:
        return jsonify({'error': 'Query text is required'}), 400

    try:
        # Generate embedding for query
        emb = get_embedder()
        query_embedding = emb.generate_embedding(query_text)

        # Get all documents with embeddings
        cursor = db.conn.cursor()
        cursor.execute("SELECT id, metadata_json, embedding_json FROM documents WHERE embedding_json IS NOT NULL")

        similarities = []
        for row in cursor.fetchall():
            doc_id, metadata_json, embedding_json = row
            doc_embedding = json.loads(embedding_json)

            similarity = cosine_similarity(query_embedding, doc_embedding)
            metadata = json.loads(metadata_json)

            similarities.append({
                'id': doc_id,
                'title': metadata.get('title', 'Untitled'),
                'language': metadata.get('language', 'unknown'),
                'topics': metadata.get('topics', []),
                'summary': metadata.get('summary', ''),
                'similarity': round(similarity, 4)
            })

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)

        return jsonify({
            'query': query_text,
            'total_results': len(similarities[:limit]),
            'results': similarities[:limit]
        })

    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/document/<int:doc_id>')
def get_document(doc_id):
    """Get full document details"""
    cursor = db.conn.cursor()
    cursor.execute(
        "SELECT id, content, metadata_json, embedding_json, created_at FROM documents WHERE id = ?",
        (doc_id,)
    )

    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Document not found'}), 404

    doc_id, content, metadata_json, embedding_json, created_at = row
    metadata = json.loads(metadata_json)

    return jsonify({
        'id': doc_id,
        'content': content,
        'metadata': metadata,
        'has_embedding': embedding_json is not None,
        'created_at': created_at
    })


@app.route('/api/similar/<int:doc_id>')
def find_similar(doc_id):
    """Find documents similar to a given document"""
    limit = int(request.args.get('limit', 5))

    # Get document embedding
    cursor = db.conn.cursor()
    cursor.execute("SELECT embedding_json, metadata_json FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()

    if not row or not row[0]:
        return jsonify({'error': 'Document not found or has no embedding'}), 404

    query_embedding = json.loads(row[0])
    query_metadata = json.loads(row[1])

    # Find similar documents
    cursor.execute("SELECT id, metadata_json, embedding_json FROM documents WHERE id != ? AND embedding_json IS NOT NULL", (doc_id,))

    similarities = []
    for row in cursor.fetchall():
        other_id, metadata_json, embedding_json = row
        doc_embedding = json.loads(embedding_json)

        similarity = cosine_similarity(query_embedding, doc_embedding)
        metadata = json.loads(metadata_json)

        similarities.append({
            'id': other_id,
            'title': metadata.get('title', 'Untitled'),
            'language': metadata.get('language', 'unknown'),
            'topics': metadata.get('topics', []),
            'summary': metadata.get('summary', ''),
            'similarity': round(similarity, 4)
        })

    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    return jsonify({
        'source_document': {
            'id': doc_id,
            'title': query_metadata.get('title', 'Untitled')
        },
        'similar_documents': similarities[:limit]
    })


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    cursor = db.conn.cursor()

    # Total documents
    cursor.execute("SELECT COUNT(*) FROM documents")
    total = cursor.fetchone()[0]

    # Documents with embeddings
    cursor.execute("SELECT COUNT(*) FROM documents WHERE embedding_json IS NOT NULL")
    with_embeddings = cursor.fetchone()[0]

    # Get all metadata for analysis
    cursor.execute("SELECT metadata_json FROM documents")
    languages = {}
    topics = {}

    for row in cursor.fetchall():
        metadata = json.loads(row[0])

        lang = metadata.get('language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1

        for topic in metadata.get('topics', []):
            topics[topic] = topics.get(topic, 0) + 1

    # Top 20 topics
    top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:20]

    return jsonify({
        'total_documents': total,
        'documents_with_embeddings': with_embeddings,
        'languages': languages,
        'top_topics': [{'topic': t[0], 'count': t[1]} for t in top_topics]
    })


@app.route('/api/browse')
def browse():
    """Browse all documents with pagination"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    language = request.args.get('lang', '')
    topic = request.args.get('topic', '')

    offset = (page - 1) * per_page

    # Build query with filters
    sql = "SELECT id, metadata_json, created_at FROM documents WHERE 1=1"
    params = []

    if language:
        sql += " AND metadata_json LIKE ?"
        params.append(f'%"language": "{language}"%')

    if topic:
        sql += " AND metadata_json LIKE ?"
        params.append(f'%{topic}%')

    sql += f" ORDER BY created_at DESC LIMIT {per_page} OFFSET {offset}"

    cursor = db.conn.cursor()
    cursor.execute(sql, params)

    documents = []
    for row in cursor.fetchall():
        doc_id, metadata_json, created_at = row
        metadata = json.loads(metadata_json)

        documents.append({
            'id': doc_id,
            'title': metadata.get('title', 'Untitled'),
            'language': metadata.get('language', 'unknown'),
            'topics': metadata.get('topics', []),
            'summary': metadata.get('summary', ''),
            'keywords': metadata.get('keywords', [])[:10],  # First 10 keywords
            'created_at': created_at
        })

    # Get total count for pagination
    count_sql = "SELECT COUNT(*) FROM documents WHERE 1=1"
    if language:
        count_sql += " AND metadata_json LIKE ?"
    if topic:
        count_sql += " AND metadata_json LIKE ?"

    cursor.execute(count_sql, params if params else [])
    total = cursor.fetchone()[0]

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'documents': documents
    })


# Create templates directory if it doesn't exist
templates_dir = Path(__file__).parent / 'templates'
templates_dir.mkdir(exist_ok=True)

# Create simple HTML template
html_template = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Never-Tired-Archaeologist - Document Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .stats {
            display: flex;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .stat-box {
            background: #f8f9fa;
            padding: 15px 25px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            font-size: 14px;
        }

        .search-box {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        .search-input {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            transition: border-color 0.3s;
        }

        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .search-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: #f8f9fa;
            color: #333;
            border: 2px solid #e0e0e0;
        }

        .btn-secondary:hover {
            background: #e9ecef;
        }

        .filters {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        select {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }

        .results {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .result-item {
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
            cursor: pointer;
            transition: background 0.3s;
        }

        .result-item:hover {
            background: #f8f9fa;
        }

        .result-item:last-child {
            border-bottom: none;
        }

        .result-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }

        .result-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 14px;
        }

        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge-language {
            background: #667eea;
            color: white;
        }

        .badge-topic {
            background: #e9ecef;
            color: #495057;
        }

        .result-summary {
            color: #666;
            line-height: 1.6;
        }

        .similarity-score {
            color: #667eea;
            font-weight: bold;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            overflow-y: auto;
        }

        .modal-content {
            background: white;
            max-width: 900px;
            margin: 50px auto;
            padding: 40px;
            border-radius: 15px;
        }

        .close-modal {
            float: right;
            font-size: 30px;
            cursor: pointer;
            color: #999;
        }

        .close-modal:hover {
            color: #333;
        }

        .content-preview {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Never-Tired-Archaeologist</h1>
            <p>Intelligente Dokumentensuche mit KI-gestützter Analyse</p>

            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{{ stats.total_documents }}</div>
                    <div class="stat-label">Dokumente</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ stats.languages|length }}</div>
                    <div class="stat-label">Sprachen</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ stats.topics|length }}</div>
                    <div class="stat-label">Topics</div>
                </div>
            </div>
        </header>

        <div class="search-box">
            <input type="text"
                   id="searchInput"
                   class="search-input"
                   placeholder="Suche nach Dokumenten..."
                   onkeypress="if(event.key === 'Enter') textSearch()">

            <div class="filters">
                <select id="languageFilter">
                    <option value="">Alle Sprachen</option>
                    {% for lang in stats.languages %}
                    <option value="{{ lang }}">{{ lang }}</option>
                    {% endfor %}
                </select>

                <select id="topicFilter">
                    <option value="">Alle Topics</option>
                    {% for topic in stats.topics %}
                    <option value="{{ topic }}">{{ topic }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="search-buttons">
                <button class="btn btn-primary" onclick="textSearch()">🔎 Textsuche</button>
                <button class="btn btn-primary" onclick="semanticSearch()">🧠 Semantische Suche</button>
                <button class="btn btn-secondary" onclick="browseAll()">📚 Alle durchsuchen</button>
            </div>
        </div>

        <div class="results" id="results" style="display: none;">
            <h2 id="resultsTitle">Ergebnisse</h2>
            <div id="resultsContainer"></div>
        </div>
    </div>

    <div id="documentModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        async function textSearch() {
            const query = document.getElementById('searchInput').value;
            const lang = document.getElementById('languageFilter').value;
            const topic = document.getElementById('topicFilter').value;

            if (!query) {
                alert('Bitte geben Sie einen Suchbegriff ein');
                return;
            }

            showLoading();

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&lang=${lang}&topic=${encodeURIComponent(topic)}`);
                const data = await response.json();
                displayResults(data.results, `Textsuche: "${query}" (${data.total_results} Ergebnisse)`);
            } catch (error) {
                alert('Fehler bei der Suche: ' + error);
            }
        }

        async function semanticSearch() {
            const query = document.getElementById('searchInput').value;

            if (!query) {
                alert('Bitte geben Sie einen Suchbegriff ein');
                return;
            }

            showLoading();

            try {
                const response = await fetch('/api/semantic-search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                const data = await response.json();
                displayResults(data.results, `Semantische Suche: "${query}" (${data.total_results} Ergebnisse)`, true);
            } catch (error) {
                alert('Fehler bei der Suche: ' + error);
            }
        }

        async function browseAll() {
            const lang = document.getElementById('languageFilter').value;
            const topic = document.getElementById('topicFilter').value;

            showLoading();

            try {
                const response = await fetch(`/api/browse?lang=${lang}&topic=${encodeURIComponent(topic)}`);
                const data = await response.json();
                displayResults(data.documents, `Dokumente (${data.total} gesamt)`);
            } catch (error) {
                alert('Fehler beim Laden: ' + error);
            }
        }

        function showLoading() {
            const results = document.getElementById('results');
            const container = document.getElementById('resultsContainer');
            results.style.display = 'block';
            container.innerHTML = '<div class="loading">⏳ Lade Ergebnisse...</div>';
        }

        function displayResults(results, title, showSimilarity = false) {
            const resultsDiv = document.getElementById('results');
            const titleDiv = document.getElementById('resultsTitle');
            const container = document.getElementById('resultsContainer');

            resultsDiv.style.display = 'block';
            titleDiv.textContent = title;

            if (results.length === 0) {
                container.innerHTML = '<p>Keine Ergebnisse gefunden.</p>';
                return;
            }

            let html = '';
            results.forEach(doc => {
                html += `
                    <div class="result-item" onclick="showDocument(${doc.id})">
                        <div class="result-title">${escapeHtml(doc.title)}</div>
                        <div class="result-meta">
                            <span class="badge badge-language">${doc.language}</span>
                            ${doc.topics.slice(0, 3).map(t => `<span class="badge badge-topic">${escapeHtml(t)}</span>`).join('')}
                            ${showSimilarity ? `<span class="similarity-score">Ähnlichkeit: ${(doc.similarity * 100).toFixed(1)}%</span>` : ''}
                        </div>
                        <div class="result-summary">${escapeHtml(doc.summary || 'Keine Zusammenfassung verfügbar')}</div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        async function showDocument(docId) {
            try {
                const response = await fetch(`/api/document/${docId}`);
                const doc = await response.json();

                let html = `
                    <h2>${escapeHtml(doc.metadata.title)}</h2>
                    <div style="margin: 20px 0;">
                        <span class="badge badge-language">${doc.metadata.language}</span>
                        ${doc.metadata.topics.map(t => `<span class="badge badge-topic">${escapeHtml(t)}</span>`).join(' ')}
                    </div>
                    <h3>Zusammenfassung</h3>
                    <p>${escapeHtml(doc.metadata.summary)}</p>
                    <h3>Keywords</h3>
                    <p>${doc.metadata.keywords.join(', ')}</p>
                    <h3>Inhalt</h3>
                    <div class="content-preview">${escapeHtml(doc.content)}</div>
                    <button class="btn btn-primary" style="margin-top: 20px;" onclick="findSimilar(${docId})">Ähnliche Dokumente finden</button>
                `;

                document.getElementById('modalContent').innerHTML = html;
                document.getElementById('documentModal').style.display = 'block';
            } catch (error) {
                alert('Fehler beim Laden des Dokuments: ' + error);
            }
        }

        async function findSimilar(docId) {
            closeModal();
            showLoading();

            try {
                const response = await fetch(`/api/similar/${docId}`);
                const data = await response.json();
                displayResults(data.similar_documents, `Ähnliche Dokumente zu: ${data.source_document.title}`, true);
            } catch (error) {
                alert('Fehler: ' + error);
            }
        }

        function closeModal() {
            document.getElementById('documentModal').style.display = 'none';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Close modal on outside click
        window.onclick = function(event) {
            const modal = document.getElementById('documentModal');
            if (event.target === modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>"""

# Save HTML template
(templates_dir / 'index.html').write_text(html_template, encoding='utf-8')


def main():
    """Start web server"""
    print("=" * 70)
    print("Never-Tired-Archaeologist Web Interface")
    print("=" * 70)
    print("\n🚀 Starting web server...")
    print("📍 URL: http://localhost:5000")
    print("\n✨ Features:")
    print("  - Volltextsuche")
    print("  - Semantische Suche (Ähnlichkeitssuche)")
    print("  - Filter nach Sprache und Topics")
    print("  - Dokument-Details mit Volltext")
    print("  - Ähnliche Dokumente finden")
    print("\n⏹️  Drücken Sie CTRL+C zum Beenden\n")
    print("=" * 70)

    app.run(debug=False, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
