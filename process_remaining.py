"""
Process Remaining Failed Documents
Processes the 8 documents that failed during the initial batch run
"""

import sys
import time
import logging
from pathlib import Path

from src.database import DocDatabase
from src.embedder import LocalEmbedder
from src.llm import Analyzer
from src.models import DocumentMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# The 8 failed documents from resources2
FAILED_DOCUMENTS = [
    "Vereinfachte_Confiforms-Lösung_für_Jira-Epic-Erstellung.md",
    "Verlauf_Promtingqueen_Gemini.md",
    "virtual_functions.md",
    "Wichtige_Links_ConfiForms.md",
    "zed-ai-providers-setup.md",
    "zed-installation-guide.md",
    "zed-settings.md",
    "Zusammenfassung_der_Analyse-Ergebnisse.md"
]

def process_document(filepath: Path, db: DocDatabase, embedder: LocalEmbedder, analyzer: Analyzer):
    """Process a single document"""

    logger.info(f"Processing: {filepath.name}")

    try:
        # Read file
        try:
            content = filepath.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = filepath.read_text(encoding='latin-1')

        logger.info(f"  Length: {len(content)} characters")

        # Check for duplicates
        content_hash = db._compute_hash(content)
        if db.document_exists(content_hash):
            logger.info(f"  [SKIP] Already in database")
            return True

        # Generate embedding
        logger.info(f"  Generating embedding...")
        embedding = embedder.generate_embedding(content)

        # Analyze with Claude
        logger.info(f"  Analyzing with Claude...")
        metadata = analyzer.analyze_text(content)

        # Store in database
        doc_id = db.add_document(content, metadata, embedding)

        logger.info(f"  [OK] Stored with ID: {doc_id}")
        logger.info(f"  Title: {metadata.title}")
        logger.info(f"  Language: {metadata.language}")
        logger.info(f"  Topics: {', '.join(metadata.topics[:3])}")

        return True

    except Exception as e:
        logger.error(f"  [ERROR] Failed: {e}")
        return False

def main():
    """Main entry point"""

    print("=" * 70)
    print("Processing Remaining Failed Documents")
    print("=" * 70)
    print()

    # Initialize components
    logger.info("Initializing database...")
    db = DocDatabase()

    logger.info("Loading embedding model...")
    embedder = LocalEmbedder()

    logger.info("Initializing Claude analyzer...")
    analyzer = Analyzer()

    print()
    print(f"Found {len(FAILED_DOCUMENTS)} documents to process")
    print()

    # Base path for resources2
    resources2_path = Path("../resources2")

    if not resources2_path.exists():
        print(f"ERROR: Directory not found: {resources2_path.absolute()}")
        sys.exit(1)

    # Process each document
    success_count = 0
    skip_count = 0
    fail_count = 0

    for i, filename in enumerate(FAILED_DOCUMENTS, 1):
        print(f"\n[{i}/{len(FAILED_DOCUMENTS)}] {filename}")
        print("-" * 70)

        filepath = resources2_path / filename

        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            fail_count += 1
            continue

        result = process_document(filepath, db, embedder, analyzer)

        if result:
            success_count += 1
        else:
            fail_count += 1

        # Small delay to avoid rate limiting
        if i < len(FAILED_DOCUMENTS):
            time.sleep(1)

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total:      {len(FAILED_DOCUMENTS)}")
    print(f"Successful: {success_count}")
    print(f"Skipped:    {skip_count}")
    print(f"Failed:     {fail_count}")
    print("=" * 70)

    if fail_count > 0:
        print()
        print("⚠ Some documents failed. Check logs above for details.")
        sys.exit(1)
    else:
        print()
        print("✓ All documents processed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
