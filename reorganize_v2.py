"""
Reorganize Documents into 12 Main Categories - Version 2
Uses database metadata to categorize and moves files from original resources2 folder
"""

import sqlite3
import json
import shutil
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def analyze_documents():
    """Analyze all documents from database"""

    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()

    # Get documents from resources2 (IDs 9-132, excluding test docs 1-8)
    cursor.execute("""
        SELECT id, content, metadata_json, created_at
        FROM documents
        WHERE id >= 9
        ORDER BY id
    """)

    documents = []

    for row in cursor.fetchall():
        doc_id, content, metadata_json, created_at = row
        metadata = json.loads(metadata_json)

        documents.append({
            'id': doc_id,
            'title': metadata.get('title', ''),
            'language': metadata.get('language', 'unknown'),
            'topics': metadata.get('topics', []),
            'keywords': metadata.get('keywords', []),
            'content_hash': content[:100]  # For matching
        })

    conn.close()

    return documents


def create_category_mapping():
    """Define 12 main categories with their matching rules"""

    categories = {
        'Confluence-ConfiForms': {
            'keywords': ['confiforms', 'confluence', 'atlassian confluence'],
            'priority': 1
        },
        'Jira-Integration': {
            'keywords': ['jira', 'epic', 'issue', 'rest api'],
            'priority': 2
        },
        'Prompt-Engineering': {
            'keywords': ['prompt', 'system prompt', 'prompting', 'prompter'],
            'priority': 3
        },
        'Software-Entwicklung': {
            'keywords': ['plugin', 'entwicklung', 'development', 'firefox', 'chrome', 'extension'],
            'priority': 4
        },
        'Dokumentation-Anleitungen': {
            'keywords': ['dokumentation', 'documentation', 'anleitung', 'guide', 'tutorial', 'benutzeranleitung'],
            'priority': 5
        },
        'Projektmanagement': {
            'keywords': ['projekt', 'deliverable', 'checkliste', 'todo', 'anforderung', 'requirement'],
            'priority': 6
        },
        'Testing-QA': {
            'keywords': ['test', 'testing', 'qualität', 'quality', 'validierung', 'validation', 'qa'],
            'priority': 7
        },
        'Konfiguration-Setup': {
            'keywords': ['konfiguration', 'configuration', 'setup', 'installation', 'config', 'zed', 'editor'],
            'priority': 8
        },
        'UI-UX-Design': {
            'keywords': ['ui', 'ux', 'benutzeroberfläche', 'design', 'interface', 'preview'],
            'priority': 9
        },
        'AI-KI-Tools': {
            'keywords': ['ai', 'ki', 'claude', 'artificial intelligence', 'machine learning', 'primer', 'template'],
            'priority': 10
        },
        'Workflow-Automation': {
            'keywords': ['workflow', 'automation', 'ifttt', 'automatisierung', 'bidirektional'],
            'priority': 11
        },
        'Sonstiges': {
            'keywords': ['oracle', 'database', 'zeit', 'troubleshooting', 'links', 'key', 'license'],
            'priority': 12
        }
    }

    return categories


def assign_category(doc, categories):
    """Assign best matching category to a document"""

    # Combine searchable text
    searchable = (
        doc['title'].lower() + ' ' +
        ' '.join(doc['topics']).lower() + ' ' +
        ' '.join(doc['keywords']).lower()
    )

    # Find matches with priority
    matches = []

    for category, config in categories.items():
        match_count = 0
        for keyword in config['keywords']:
            if keyword in searchable:
                match_count += 1

        if match_count > 0:
            matches.append({
                'category': category,
                'score': match_count,
                'priority': config['priority']
            })

    if matches:
        # Sort by score (descending), then priority (ascending)
        matches.sort(key=lambda x: (-x['score'], x['priority']))
        return matches[0]['category']

    return 'Sonstiges'


def find_source_file(doc_title, source_dir):
    """Find source file by fuzzy matching title"""

    # Normalize title
    normalized_title = doc_title.lower().replace(' ', '_').replace('-', '_').replace(':', '').replace('?', '')

    # Search for .md files
    for file in source_dir.glob('*.md'):
        file_name_lower = file.stem.lower().replace(' ', '_').replace('-', '_')

        # Try various matching strategies
        if file_name_lower == normalized_title:
            return file

        # Check if one contains the other
        if normalized_title in file_name_lower or file_name_lower in normalized_title:
            return file

        # Check significant words (>4 chars)
        title_words = set(w for w in normalized_title.split('_') if len(w) > 4)
        file_words = set(w for w in file_name_lower.split('_') if len(w) > 4)

        if title_words and file_words:
            overlap = len(title_words & file_words) / len(title_words)
            if overlap > 0.5:  # 50% word overlap
                return file

    return None


def reorganize_files():
    """Main reorganization function"""

    logger.info("=" * 70)
    logger.info("REORGANIZING DOCUMENTS INTO 12 CATEGORIES")
    logger.info("=" * 70)
    logger.info("")

    # Analyze documents
    logger.info("Analyzing documents from database...")
    documents = analyze_documents()
    logger.info(f"Found {len(documents)} documents (excluding test docs)")
    logger.info("")

    # Create category mapping
    categories = create_category_mapping()

    # Assign categories
    logger.info("Assigning categories...")
    category_assignments = defaultdict(list)

    for doc in documents:
        category = assign_category(doc, categories)
        category_assignments[category].append(doc)

    # Print distribution
    logger.info("")
    logger.info("Category Distribution:")
    logger.info("-" * 70)
    total = 0
    for category in sorted(categories.keys()):
        count = len(category_assignments[category])
        total += count
        logger.info(f"  {category:35} {count:3} documents")
    logger.info(f"  {'TOTAL':35} {total:3} documents")
    logger.info("")

    # Confirm
    response = input("Proceed with reorganization? (yes/no): ").strip().lower()
    if response not in ['yes', 'y', 'ja', 'j']:
        logger.info("Cancelled.")
        return

    # Setup directories
    source_dir = Path("../resources2")
    target_dir = Path("../resources2_final")

    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir.absolute()}")
        return

    logger.info("")
    logger.info(f"Source: {source_dir.absolute()}")
    logger.info(f"Target: {target_dir.absolute()}")
    logger.info("")

    # Create target directory
    target_dir.mkdir(exist_ok=True)

    # Move files
    logger.info("Copying files to new structure...")
    logger.info("")

    moved_count = 0
    not_found_count = 0
    skipped_files = []

    for category, docs in sorted(category_assignments.items()):
        if not docs:
            continue

        logger.info(f"📁 {category}")

        # Create category directory
        category_dir = target_dir / category
        category_dir.mkdir(exist_ok=True)

        for doc in sorted(docs, key=lambda x: x['title']):
            source_file = find_source_file(doc['title'], source_dir)

            if source_file:
                target_file = category_dir / source_file.name

                try:
                    shutil.copy2(source_file, target_file)
                    logger.info(f"   ✓ {source_file.name}")
                    moved_count += 1
                except Exception as e:
                    logger.error(f"   ✗ Error: {e}")
            else:
                logger.warning(f"   ? Not found: {doc['title'][:60]}...")
                not_found_count += 1
                skipped_files.append(doc['title'])

        logger.info("")

    # Create index
    create_index(target_dir, category_assignments)

    # Summary
    logger.info("=" * 70)
    logger.info("REORGANIZATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Files copied:     {moved_count}")
    logger.info(f"Files not found:  {not_found_count}")
    logger.info(f"Total documents:  {len(documents)}")
    logger.info(f"Output directory: {target_dir.absolute()}")
    logger.info("=" * 70)

    if skipped_files:
        logger.info("")
        logger.info("Files not found (first 10):")
        for title in skipped_files[:10]:
            logger.info(f"  - {title[:70]}")
        if len(skipped_files) > 10:
            logger.info(f"  ... and {len(skipped_files) - 10} more")


def create_index(target_dir, category_assignments):
    """Create index file"""

    index_path = target_dir / "INDEX.md"

    lines = ["# Document Organization - 12 Categories\n\n"]
    lines.append("Reorganized based on AI-analyzed metadata\n\n")
    lines.append("## Categories\n\n")

    for category in sorted(category_assignments.keys()):
        docs = category_assignments[category]
        if not docs:
            continue

        lines.append(f"### {category} ({len(docs)} documents)\n\n")

        for doc in sorted(docs, key=lambda x: x['title'])[:15]:
            lines.append(f"- {doc['title']}\n")

        if len(docs) > 15:
            lines.append(f"- ... and {len(docs) - 15} more\n")

        lines.append("\n")

    # Add statistics
    total = sum(len(docs) for docs in category_assignments.values())
    lines.append(f"## Statistics\n\n")
    lines.append(f"- Total documents: {total}\n")
    lines.append(f"- Categories: {len([c for c, d in category_assignments.items() if d])}\n")

    index_path.write_text("".join(lines), encoding='utf-8')
    logger.info(f"Created index: {index_path}")


if __name__ == "__main__":
    reorganize_files()
