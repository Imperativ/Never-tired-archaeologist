"""
Simple Web Interface for Never-Tired-Archaeologist
Minimal Flask app for testing
"""

from flask import Flask, jsonify
import sqlite3
import json

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Search</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            h1 { color: #333; }
            .search-box {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            input {
                width: 70%;
                padding: 10px;
                font-size: 16px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover { background: #0056b3; }
            .results {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .doc {
                padding: 15px;
                border-bottom: 1px solid #eee;
            }
            .doc:last-child { border-bottom: none; }
            .doc-title {
                font-size: 18px;
                font-weight: bold;
                color: #007bff;
                margin-bottom: 5px;
            }
            .doc-meta {
                color: #666;
                font-size: 14px;
                margin-bottom: 5px;
            }
            .badge {
                display: inline-block;
                padding: 3px 8px;
                background: #e9ecef;
                border-radius: 3px;
                font-size: 12px;
                margin-right: 5px;
            }
            .stats {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <h1>🔍 Document Search</h1>

        <div class="stats" id="stats">Loading statistics...</div>

        <div class="search-box">
            <input type="text" id="query" placeholder="Search documents..." onkeypress="if(event.key==='Enter') search()">
            <button onclick="search()">Search</button>
            <button onclick="browseAll()">Browse All</button>
        </div>

        <div class="results" id="results" style="display:none;"></div>

        <script>
            loadStats();

            async function loadStats() {
                try {
                    const res = await fetch('/api/stats');
                    const data = await res.json();
                    document.getElementById('stats').innerHTML = `
                        <strong>Database:</strong> ${data.total} documents |
                        <strong>Languages:</strong> ${Object.keys(data.languages).join(', ')} |
                        <strong>Top Topics:</strong> ${data.top_topics.slice(0,5).map(t => t.topic).join(', ')}
                    `;
                } catch(e) {
                    document.getElementById('stats').innerHTML = 'Error loading stats: ' + e;
                }
            }

            async function search() {
                const query = document.getElementById('query').value;
                if (!query) return alert('Please enter a search term');

                try {
                    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    displayResults(data.results, `Search: "${query}" (${data.total} results)`);
                } catch(e) {
                    alert('Search failed: ' + e);
                }
            }

            async function browseAll() {
                try {
                    const res = await fetch('/api/browse?limit=20');
                    const data = await res.json();
                    displayResults(data.documents, `All Documents (${data.total} total)`);
                } catch(e) {
                    alert('Browse failed: ' + e);
                }
            }

            function displayResults(docs, title) {
                const div = document.getElementById('results');
                div.style.display = 'block';

                if (docs.length === 0) {
                    div.innerHTML = '<h2>' + title + '</h2><p>No results found.</p>';
                    return;
                }

                let html = '<h2>' + title + '</h2>';
                docs.forEach(doc => {
                    html += `
                        <div class="doc">
                            <div class="doc-title">${escapeHtml(doc.title)}</div>
                            <div class="doc-meta">
                                <span class="badge">${doc.language}</span>
                                ${(doc.topics || []).slice(0,3).map(t => `<span class="badge">${escapeHtml(t)}</span>`).join('')}
                            </div>
                            <div>${escapeHtml(doc.summary || 'No summary available')}</div>
                        </div>
                    `;
                });

                div.innerHTML = html;
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/stats')
def stats():
    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT metadata_json FROM documents")
    languages = {}
    topics = {}

    for row in cursor.fetchall():
        meta = json.loads(row[0])
        lang = meta.get('language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1

        for topic in meta.get('topics', []):
            topics[topic] = topics.get(topic, 0) + 1

    conn.close()

    top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify({
        'total': total,
        'languages': languages,
        'top_topics': [{'topic': t[0], 'count': t[1]} for t in top_topics]
    })

@app.route('/api/search')
def search():
    from flask import request
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))

    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, metadata_json FROM documents
           WHERE content LIKE ? OR metadata_json LIKE ?
           LIMIT ?""",
        (f'%{query}%', f'%{query}%', limit)
    )

    results = []
    for row in cursor.fetchall():
        doc_id, meta_json = row
        meta = json.loads(meta_json)
        results.append({
            'id': doc_id,
            'title': meta.get('title', 'Untitled'),
            'language': meta.get('language', 'unknown'),
            'topics': meta.get('topics', []),
            'summary': meta.get('summary', '')
        })

    conn.close()

    return jsonify({
        'query': query,
        'total': len(results),
        'results': results
    })

@app.route('/api/browse')
def browse():
    from flask import request
    limit = int(request.args.get('limit', 20))

    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT id, metadata_json FROM documents ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )

    documents = []
    for row in cursor.fetchall():
        doc_id, meta_json = row
        meta = json.loads(meta_json)
        documents.append({
            'id': doc_id,
            'title': meta.get('title', 'Untitled'),
            'language': meta.get('language', 'unknown'),
            'topics': meta.get('topics', []),
            'summary': meta.get('summary', '')
        })

    conn.close()

    return jsonify({
        'total': total,
        'documents': documents
    })

if __name__ == '__main__':
    print("=" * 70)
    print("Simple Document Search Interface")
    print("=" * 70)
    print("\nStarting server...")
    print("URL: http://localhost:5000")
    print("\nPress CTRL+C to stop")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)
