"""
Never-Tired-Archaeologist - Main Pipeline

Semantic document analysis tool combining:
- Local embeddings (sentence-transformers)
- LLM analysis (Anthropic Claude)
- SQLite storage
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from src import DocumentMetadata, DocDatabase, LocalEmbedder, Analyzer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('archaeologist.log')
    ]
)

logger = logging.getLogger(__name__)


def read_text_file(file_path: str) -> str:
    """
    Read content from a text file.

    Args:
        file_path: Path to the text file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            raise ValueError(f"File is empty: {file_path}")

        logger.info(f"Read {len(content)} characters from {file_path}")
        return content

    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
            logger.warning(f"File read with latin-1 encoding: {file_path}")
            return content
        except Exception as e:
            raise RuntimeError(f"Could not read file {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading file {file_path}: {e}")


def compute_content_hash(content: str) -> str:
    """
    Compute SHA256 hash of content.

    Args:
        content: Text content

    Returns:
        Hexadecimal hash string
    """
    import hashlib
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def process_document(
    file_path: str,
    db: DocDatabase,
    embedder: LocalEmbedder,
    analyzer: Analyzer,
    force_reprocess: bool = False
) -> Optional[DocumentMetadata]:
    """
    Process a single document through the complete pipeline.

    Steps:
    1. Read file content
    2. Check if document already exists (via hash)
    3. Generate embedding (local)
    4. Analyze with Claude API
    5. Store in database
    6. Return extracted metadata

    Args:
        file_path: Path to document file
        db: Database instance
        embedder: Embedding generator
        analyzer: LLM analyzer
        force_reprocess: If True, process even if document exists

    Returns:
        DocumentMetadata if processing was successful, None if skipped (duplicate)
    """
    logger.info(f"{'='*60}")
    logger.info(f"Processing: {file_path}")
    logger.info(f"{'='*60}")

    try:
        # Step 1: Read file
        content = read_text_file(file_path)
        content_hash = compute_content_hash(content)
        logger.info(f"Content hash: {content_hash[:16]}...")

        # Step 2: Check for duplicates
        if not force_reprocess and db.document_exists(content_hash):
            logger.warning(f"[WARNING] Document already exists in database (hash: {content_hash[:16]}...)")
            logger.info("Skipping processing. Use --force to reprocess.")
            return None

        # Step 3: Generate embedding (local)
        logger.info("Generating embedding (local)...")
        embedding = embedder.generate_embedding(content)
        logger.info(f"[OK] Embedding generated ({len(embedding)} dimensions)")

        # Step 4: Analyze with Claude
        logger.info("Analyzing document with Claude API...")
        metadata = analyzer.analyze_text(content)
        logger.info(f"[OK] Analysis complete: {metadata.title}")

        # Step 5: Store in database
        logger.info("Storing in database...")
        doc_id = db.add_document(
            content=content,
            metadata=metadata,
            embedding=embedding
        )
        logger.info(f"[OK] Document stored with ID: {doc_id}")

        # Step 6: Display results
        print("\n" + "="*60)
        print("EXTRACTED METADATA")
        print("="*60)
        print(f"Title:    {metadata.title}")
        print(f"Language: {metadata.language}")
        print(f"Topics:   {', '.join(metadata.topics)}")
        print(f"Keywords: {', '.join(metadata.keywords)}")
        print(f"\nSummary:\n{metadata.summary}")
        print("="*60)
        print(f"[OK] Document ID: {doc_id}")
        print(f"[OK] Embedding: {len(embedding)} dimensions")
        print("="*60 + "\n")

        return metadata

    except FileNotFoundError as e:
        logger.error(f"[ERROR] File not found: {e}")
        return None
    except ValueError as e:
        logger.error(f"[ERROR] Value error: {e}")
        return None
    except RuntimeError as e:
        logger.error(f"[ERROR] Processing failed: {e}")
        return None
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {e}", exc_info=True)
        return None


def main():
    """
    Main entry point for the document analysis pipeline.

    Usage:
        python main.py <file_path>
        python main.py <file_path> --force
    """
    print("\n" + "="*60)
    print("NEVER-TIRED-ARCHAEOLOGIST v2.0")
    print("Semantic Document Analysis Tool")
    print("="*60 + "\n")

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path> [--force]")
        print("\nOptions:")
        print("  --force    Reprocess document even if it already exists")
        print("\nExample:")
        print("  python main.py document.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    force_reprocess = "--force" in sys.argv

    try:
        # Initialize components
        logger.info("Initializing components...")

        # Database
        db = DocDatabase("archaeologist.db")
        logger.info("[OK] Database initialized")

        # Embedder (local)
        logger.info("Loading embedding model (this may take a moment on first run)...")
        embedder = LocalEmbedder()
        logger.info(f"[OK] Embedder ready (dimension: {embedder.get_embedding_dimension()})")

        # Analyzer (Claude API)
        analyzer = Analyzer()
        logger.info(f"[OK] Analyzer ready ({analyzer.get_model_info()['model']})")

        # Process document
        metadata = process_document(
            file_path=file_path,
            db=db,
            embedder=embedder,
            analyzer=analyzer,
            force_reprocess=force_reprocess
        )

        if metadata is None:
            logger.info("No processing performed (document may be duplicate)")
        else:
            logger.info("[OK] Processing completed successfully")

        # Close database
        db.close()
        logger.info("Database connection closed")

    except KeyboardInterrupt:
        print("\n\n[WARNING] Process interrupted by user")
        logger.warning("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n[ERROR] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
