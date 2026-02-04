"""
Reorganize Documents into 12 Main Categories
Analyzes existing metadata from database and creates optimized folder structure
"""

import sqlite3
import json
import shutil
from pathlib import Path
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def analyze_documents():
    """Analyze all documents from database to determine best categories"""

    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()

    # Get all documents with metadata
    cursor.execute("SELECT id, metadata_json FROM documents")

    all_topics = []
    documents = []

    for row in cursor.fetchall():
        doc_id, metadata_json = row
        metadata = json.loads(metadata_json)

        documents.append({
            'id': doc_id,
            'title': metadata.get('title', ''),
            'language': metadata.get('language', 'unknown'),
            'topics': metadata.get('topics', []),
            'keywords': metadata.get('keywords', [])
        })

        # Collect all topics
        all_topics.extend(metadata.get('topics', []))

    conn.close()

    # Count topic frequencies
    topic_counts = Counter(all_topics)

    return documents, topic_counts


def create_category_mapping(topic_counts):
    """Create mapping from topics to 12 main categories"""

    # Define 12 main categories with their keywords
    categories = {
        'Confluence-ConfiForms': [
            'ConfiForms', 'Confiforms', 'ConfiForms-Optimierung',
            'Confluence', 'Confiforms-Integration', 'Atlassian Confluence'
        ],
        'Jira-Integration': [
            'Jira', 'Jira Integration', 'Jira-Integration', 'Jira-Konfiguration',
            'Jira API', 'JIRA Configuration'
        ],
        'Prompt-Engineering': [
            'Prompt Engineering', 'prompt engineering', 'KI-Prompting',
            'System Prompts', 'AI prompt engineering'
        ],
        'Software-Entwicklung': [
            'Software-Entwicklung', 'Software-Implementierung', 'Softwareentwicklung',
            'Firefox Plugin Entwicklung', 'Chrome-Erweiterung', 'AI Development',
            'AI-Entwicklung'
        ],
        'Dokumentation-Anleitungen': [
            'Dokumentation', 'documentation', 'Benutzeranleitung', 'Technical Requirements',
            'Tutorials', 'Wichtige Links'
        ],
        'Projektmanagement': [
            'Projektmanagement', 'IT-Projektmanagement', 'Projekt-Deliverables',
            'Change Management', 'Requirements Engineering', 'Anforderungskategorien'
        ],
        'Testing-QA': [
            'Software Testing', 'Software-Testing', 'Qualitätssicherung',
            'Testing und Validierung', 'Test-Ergebnisse'
        ],
        'Konfiguration-Setup': [
            'Konfiguration', 'Software-Konfiguration', 'configuration',
            'Software-Installation', 'Editor-Konfiguration', 'Setup',
            'AI Assistant Configuration', 'KI-Konfiguration'
        ],
        'UI-UX-Design': [
            'UI-UX Design', 'Benutzeroberfläche', 'UI-Anpassungen',
            'Benutzeroberfläche', 'Design'
        ],
        'AI-KI-Tools': [
            'AI Assistant', 'KI', 'Claude Code', 'AI Development',
            'AI penetration testing', 'Artificial Intelligence',
            'Machine Learning'
        ],
        'Workflow-Automation': [
            'Automation', 'Workflow', 'IFTTT-Integration',
            'Workflow-Optimierung', 'Epic-Erstellung'
        ],
        'Sonstiges': [
            'Zeiterfassung', 'arbeitszeit', 'Oracle Database',
            'Troubleshooting', 'FPV Drone', 'API Keys', 'licensing'
        ]
    }

    # Create reverse mapping: topic -> category
    topic_to_category = {}

    for category, keywords in categories.items():
        for keyword in keywords:
            topic_to_category[keyword.lower()] = category

    return categories, topic_to_category


def assign_category(doc, topic_to_category):
    """Assign best category to a document"""

    # Check topics
    for topic in doc['topics']:
        topic_lower = topic.lower()
        # Exact match
        if topic_lower in topic_to_category:
            return topic_to_category[topic_lower]

        # Partial match
        for key, category in topic_to_category.items():
            if key in topic_lower or topic_lower in key:
                return category

    # Check title as fallback
    title_lower = doc['title'].lower()

    if 'confiforms' in title_lower or 'confluence' in title_lower:
        return 'Confluence-ConfiForms'
    elif 'jira' in title_lower:
        return 'Jira-Integration'
    elif 'prompt' in title_lower:
        return 'Prompt-Engineering'
    elif 'test' in title_lower or 'qualität' in title_lower:
        return 'Testing-QA'
    elif 'projekt' in title_lower:
        return 'Projektmanagement'
    elif 'ui' in title_lower or 'design' in title_lower:
        return 'UI-UX-Design'
    elif 'config' in title_lower or 'setup' in title_lower or 'installation' in title_lower:
        return 'Konfiguration-Setup'
    elif 'entwicklung' in title_lower or 'development' in title_lower or 'plugin' in title_lower:
        return 'Software-Entwicklung'
    elif 'ai' in title_lower or 'ki' in title_lower or 'claude' in title_lower:
        return 'AI-KI-Tools'
    elif 'workflow' in title_lower or 'automation' in title_lower:
        return 'Workflow-Automation'
    elif 'dokumentation' in title_lower or 'documentation' in title_lower or 'anleitung' in title_lower:
        return 'Dokumentation-Anleitungen'

    return 'Sonstiges'


def reorganize_files():
    """Reorganize files based on database metadata"""

    logger.info("=" * 70)
    logger.info("REORGANIZING DOCUMENTS INTO 12 CATEGORIES")
    logger.info("=" * 70)
    logger.info("")

    # Analyze documents
    logger.info("Analyzing documents from database...")
    documents, topic_counts = analyze_documents()
    logger.info(f"Found {len(documents)} documents")
    logger.info("")

    # Create category mapping
    categories, topic_to_category = create_category_mapping(topic_counts)

    # Assign categories
    logger.info("Assigning categories to documents...")
    category_counts = defaultdict(list)

    for doc in documents:
        category = assign_category(doc, topic_to_category)
        category_counts[category].append(doc)

    # Print category distribution
    logger.info("")
    logger.info("Category Distribution:")
    logger.info("-" * 70)
    for category in sorted(categories.keys()):
        count = len(category_counts[category])
        logger.info(f"  {category:35} {count:3} documents")
    logger.info(f"  {'Total':35} {len(documents):3} documents")
    logger.info("")

    # Ask for confirmation
    response = input("Proceed with reorganization? (yes/no): ")
    if response.lower() not in ['yes', 'y', 'ja', 'j']:
        logger.info("Cancelled.")
        return

    # Create new directory structure
    source_dir = Path("../resources2_organized")
    target_dir = Path("../resources2_reorganized")

    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        return

    logger.info("")
    logger.info(f"Source: {source_dir.absolute()}")
    logger.info(f"Target: {target_dir.absolute()}")
    logger.info("")

    # Create target directory
    target_dir.mkdir(exist_ok=True)

    # Get document ID to file mapping
    conn = sqlite3.connect('archaeologist.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, metadata_json FROM documents")

    doc_titles = {}
    for row in cursor.fetchall():
        doc_id, metadata_json = row
        metadata = json.loads(metadata_json)
        doc_titles[doc_id] = metadata.get('title', '')

    conn.close()

    # Move files
    logger.info("Reorganizing files...")
    moved_count = 0
    not_found_count = 0

    for category, docs in category_counts.items():
        # Create category directory
        category_dir = target_dir / category
        category_dir.mkdir(exist_ok=True)

        for doc in docs:
            # Find source file
            source_file = None

            # Search in source directory
            for lang_dir in source_dir.iterdir():
                if lang_dir.is_dir():
                    for topic_dir in lang_dir.iterdir():
                        if topic_dir.is_dir():
                            for file in topic_dir.iterdir():
                                if file.is_file():
                                    # Match by title (fuzzy)
                                    file_title = file.stem.replace('_', ' ').replace('-', ' ').lower()
                                    doc_title = doc['title'].replace('_', ' ').replace('-', ' ').lower()

                                    if doc_title in file_title or file_title in doc_title:
                                        source_file = file
                                        break
                        if source_file:
                            break
                if source_file:
                    break

            if source_file:
                target_file = category_dir / source_file.name

                # Copy file
                try:
                    shutil.copy2(source_file, target_file)
                    moved_count += 1
                    logger.info(f"  ✓ {source_file.name} -> {category}")
                except Exception as e:
                    logger.error(f"  ✗ Error copying {source_file.name}: {e}")
            else:
                not_found_count += 1
                logger.warning(f"  ? File not found for: {doc['title'][:50]}...")

    # Create index
    create_index(target_dir, category_counts)

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("REORGANIZATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Files moved:      {moved_count}")
    logger.info(f"Files not found:  {not_found_count}")
    logger.info(f"Output directory: {target_dir.absolute()}")
    logger.info("=" * 70)


def create_index(target_dir, category_counts):
    """Create index file for reorganized structure"""

    index_path = target_dir / "INDEX.md"

    lines = ["# Document Organization - 12 Categories\n\n"]
    lines.append(f"Generated: {Path(__file__).name}\n\n")
    lines.append("## Structure\n\n")

    for category in sorted(category_counts.keys()):
        docs = category_counts[category]
        lines.append(f"### {category} ({len(docs)} documents)\n\n")

        # List first 10 documents
        for doc in sorted(docs, key=lambda x: x['title'])[:10]:
            lines.append(f"- {doc['title']}\n")

        if len(docs) > 10:
            lines.append(f"- ... and {len(docs) - 10} more\n")

        lines.append("\n")

    index_path.write_text("".join(lines), encoding='utf-8')
    logger.info(f"Created index: {index_path}")


if __name__ == "__main__":
    reorganize_files()
