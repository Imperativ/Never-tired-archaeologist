"""
Generate static HTML search interface from database
Creates a self-contained HTML file with all document data
"""

import sqlite3
import json
from pathlib import Path

def generate_html():
    """Generate static HTML with embedded document data"""

    # Connect to database
    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()

    # Get all documents
    cursor.execute("SELECT id, content, metadata_json, created_at FROM documents ORDER BY created_at DESC")

    documents = []
    languages = {}
    topics = {}

    for row in cursor.fetchall():
        doc_id, content, metadata_json, created_at = row
        metadata = json.loads(metadata_json)

        # Collect stats
        lang = metadata.get('language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1

        for topic in metadata.get('topics', []):
            topics[topic] = topics.get(topic, 0) + 1

        # Add document
        documents.append({
            'id': doc_id,
            'title': metadata.get('title', 'Untitled'),
            'language': lang,
            'topics': metadata.get('topics', []),
            'summary': metadata.get('summary', ''),
            'keywords': metadata.get('keywords', []),
            'content': content[:500],  # First 500 chars for preview
            'created_at': created_at
        })

    conn.close()

    # Sort topics by count
    top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:50]

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Search - Never-Tired-Archaeologist</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .stats {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .stat-box {{
            background: #f8f9fa;
            padding: 15px 25px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            color: #666;
            font-size: 14px;
        }}

        .search-box {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .search-input {{
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            transition: border-color 0.3s;
        }}

        .search-input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .filters {{
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        select {{
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }}

        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 15px;
            margin-right: 10px;
        }}

        .btn-primary {{
            background: #667eea;
            color: white;
        }}

        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .results {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .result-count {{
            margin-bottom: 20px;
            color: #666;
            font-size: 14px;
        }}

        .result-item {{
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .result-item:hover {{
            background: #f8f9fa;
        }}

        .result-item:last-child {{
            border-bottom: none;
        }}

        .result-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}

        .result-meta {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge-language {{
            background: #667eea;
            color: white;
        }}

        .badge-topic {{
            background: #e9ecef;
            color: #495057;
        }}

        .result-summary {{
            color: #666;
            line-height: 1.6;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}

        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Never-Tired-Archaeologist</h1>
            <p>Intelligente Dokumentensuche</p>

            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{len(documents)}</div>
                    <div class="stat-label">Dokumente</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(languages)}</div>
                    <div class="stat-label">Sprachen</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(topics)}</div>
                    <div class="stat-label">Topics</div>
                </div>
            </div>
        </header>

        <div class="search-box">
            <input type="text"
                   id="searchInput"
                   class="search-input"
                   placeholder="Suche nach Dokumenten..."
                   onkeyup="performSearch()">

            <div class="filters">
                <select id="languageFilter" onchange="performSearch()">
                    <option value="">Alle Sprachen</option>
                    {"".join(f'<option value="{lang}">{lang} ({count})</option>' for lang, count in sorted(languages.items()))}
                </select>

                <select id="topicFilter" onchange="performSearch()">
                    <option value="">Alle Topics</option>
                    {"".join(f'<option value="{topic}">{topic} ({count})</option>' for topic, count in top_topics)}
                </select>
            </div>

            <button class="btn btn-primary" onclick="showAll()">Alle anzeigen</button>
            <button class="btn btn-primary" onclick="clearFilters()">Filter zurücksetzen</button>
        </div>

        <div class="results" id="results">
            <div class="result-count" id="resultCount"></div>
            <div id="resultsList"></div>
        </div>
    </div>

    <script>
        // Embedded document data
        const documents = {json.dumps(documents, ensure_ascii=False)};

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function performSearch() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const language = document.getElementById('languageFilter').value;
            const topic = document.getElementById('topicFilter').value;

            let filtered = documents;

            // Filter by language
            if (language) {{
                filtered = filtered.filter(doc => doc.language === language);
            }}

            // Filter by topic
            if (topic) {{
                filtered = filtered.filter(doc => doc.topics.includes(topic));
            }}

            // Filter by search query
            if (query) {{
                filtered = filtered.filter(doc => {{
                    return doc.title.toLowerCase().includes(query) ||
                           doc.summary.toLowerCase().includes(query) ||
                           doc.content.toLowerCase().includes(query) ||
                           doc.keywords.some(k => k.toLowerCase().includes(query)) ||
                           doc.topics.some(t => t.toLowerCase().includes(query));
                }});
            }}

            displayResults(filtered, query);
        }}

        function displayResults(docs, query) {{
            const countDiv = document.getElementById('resultCount');
            const listDiv = document.getElementById('resultsList');

            if (docs.length === 0) {{
                countDiv.innerHTML = 'Keine Ergebnisse gefunden';
                listDiv.innerHTML = '<div class="no-results">Versuchen Sie andere Suchbegriffe oder Filter</div>';
                return;
            }}

            countDiv.innerHTML = `${{docs.length}} Dokument(e) gefunden`;

            let html = '';
            docs.forEach(doc => {{
                const highlightedTitle = query ? highlightText(doc.title, query) : escapeHtml(doc.title);
                const highlightedSummary = query ? highlightText(doc.summary, query) : escapeHtml(doc.summary);

                html += `
                    <div class="result-item">
                        <div class="result-title">${{highlightedTitle}}</div>
                        <div class="result-meta">
                            <span class="badge badge-language">${{doc.language}}</span>
                            ${{doc.topics.slice(0, 5).map(t => `<span class="badge badge-topic">${{escapeHtml(t)}}</span>`).join('')}}
                        </div>
                        <div class="result-summary">${{highlightedSummary}}</div>
                        ${{doc.keywords.length > 0 ? `<div style="margin-top: 10px; font-size: 12px; color: #999;">Keywords: ${{doc.keywords.slice(0, 10).join(', ')}}</div>` : ''}}
                    </div>
                `;
            }});

            listDiv.innerHTML = html;
        }}

        function highlightText(text, query) {{
            if (!query) return escapeHtml(text);

            const escaped = escapeHtml(text);
            const regex = new RegExp(`(${{query}})`, 'gi');
            return escaped.replace(regex, '<mark style="background-color: yellow;">$1</mark>');
        }}

        function showAll() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('languageFilter').value = '';
            document.getElementById('topicFilter').value = '';
            displayResults(documents, '');
        }}

        function clearFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('languageFilter').value = '';
            document.getElementById('topicFilter').value = '';
            performSearch();
        }}

        // Initial display
        window.onload = function() {{
            displayResults(documents.slice(0, 20), '');
        }};
    </script>
</body>
</html>"""

    return html

if __name__ == '__main__':
    print("Generating static HTML search interface...")
    print("Reading from archaeologist.db...")

    html_content = generate_html()

    output_file = Path('document_search.html')
    output_file.write_text(html_content, encoding='utf-8')

    print(f"✓ Successfully generated: {output_file.absolute()}")
    print(f"✓ File size: {len(html_content):,} bytes")
    print("\nTo use:")
    print(f"  1. Open {output_file.absolute()} in your browser")
    print("  2. Or double-click the file")
    print("\nNo server needed - works offline!")
