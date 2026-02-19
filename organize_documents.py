"""
Document Organization Script for Never-Tired-Archaeologist

Analyzes documents and organizes them into a structured directory hierarchy
based on language and primary topic.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional
import shutil
import time
import json
from collections import defaultdict

from src.database import DocDatabase
from src.embedder import LocalEmbedder
from src.llm import Analyzer
from src.models import DocumentMetadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organize_documents.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocumentOrganizer:
    """Analyzes and organizes documents into structured directories"""

    def __init__(self, output_base: Path = Path("organized_documents")):
        """
        Initialize document organizer.

        Args:
            output_base: Base directory for organized documents
        """
        self.db = DocDatabase()
        self.embedder = LocalEmbedder()
        self.analyzer = Analyzer()
        self.output_base = output_base
        self.output_base.mkdir(exist_ok=True)

        self.stats = {
            "total_files": 0,
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "by_language": defaultdict(int),
            "by_topic": defaultdict(int),
            "processing_times": []
        }

    def get_primary_topic(self, metadata: DocumentMetadata) -> str:
        """
        Extract primary topic from metadata.

        Args:
            metadata: Document metadata

        Returns:
            Primary topic string (sanitized for filesystem)
        """
        if metadata.topics and len(metadata.topics) > 0:
            # Use first topic as primary
            topic = metadata.topics[0]
            # Sanitize for filesystem
            topic = topic.replace("/", "-").replace("\\", "-")
            topic = topic.replace(":", "-").replace("*", "-")
            topic = topic.replace("?", "").replace("<", "").replace(">", "")
            topic = topic.replace("|", "-").replace('"', "")
            return topic
        return "Uncategorized"

    def create_organized_path(self, metadata: DocumentMetadata, original_filename: str) -> Path:
        """
        Create organized path based on metadata.

        Structure: output_base/language/primary_topic/filename

        Args:
            metadata: Document metadata
            original_filename: Original filename

        Returns:
            Path object for organized location
        """
        language = metadata.language.lower() if metadata.language else "unknown"
        topic = self.get_primary_topic(metadata)

        # Create directory structure
        target_dir = self.output_base / language / topic
        target_dir.mkdir(parents=True, exist_ok=True)

        return target_dir / original_filename

    def process_file(self, filepath: Path, copy_mode: bool = True) -> Optional[Dict]:
        """
        Process a single file: analyze and organize.

        Args:
            filepath: Path to file to process
            copy_mode: If True, copy files; if False, move files

        Returns:
            Dictionary with processing results
        """
        result = {
            "filename": filepath.name,
            "original_path": str(filepath),
            "success": False,
            "error": None,
            "metadata": None,
            "organized_path": None,
            "processing_time": 0.0,
            "action": "copy" if copy_mode else "move"
        }

        start_time = time.time()

        try:
            # Read file
            try:
                content = filepath.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with different encoding
                content = filepath.read_text(encoding='latin-1')

            result["content_length"] = len(content)

            # Check for duplicates
            content_hash = self.db._compute_hash(content)
            if self.db.document_exists(content_hash):
                logger.info(f"[SKIP] {filepath.name} - already in database")
                result["error"] = "Duplicate"
                result["processing_time"] = time.time() - start_time
                self.stats["skipped"] += 1
                return result

            # Generate embedding
            embedding = self.embedder.generate_embedding(content)

            # Analyze with Claude
            metadata = self.analyzer.analyze_text(content)
            result["metadata"] = metadata.model_dump()

            # Store in database
            doc_id = self.db.add_document(content, metadata, embedding)
            result["doc_id"] = doc_id

            # Organize file
            organized_path = self.create_organized_path(metadata, filepath.name)

            if copy_mode:
                shutil.copy2(filepath, organized_path)
            else:
                shutil.move(str(filepath), organized_path)

            result["organized_path"] = str(organized_path)
            result["success"] = True
            result["processing_time"] = time.time() - start_time

            # Update statistics
            self.stats["processed"] += 1
            self.stats["by_language"][metadata.language] += 1
            self.stats["by_topic"][self.get_primary_topic(metadata)] += 1
            self.stats["processing_times"].append(result["processing_time"])

            logger.info(f"[OK] {filepath.name} -> {organized_path.relative_to(self.output_base)}")

        except Exception as e:
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            self.stats["failed"] += 1
            logger.error(f"[ERROR] {filepath.name}: {e}")

        return result

    def process_directory(
        self,
        source_dir: Path,
        file_pattern: str = "*.md",
        copy_mode: bool = True,
        max_files: Optional[int] = None
    ) -> List[Dict]:
        """
        Process all files in a directory.

        Args:
            source_dir: Source directory to process
            file_pattern: Glob pattern for files (default: *.md)
            copy_mode: If True, copy files; if False, move files
            max_files: Optional limit on number of files to process

        Returns:
            List of processing results
        """
        logger.info("=" * 70)
        logger.info("DOCUMENT ORGANIZATION STARTED")
        logger.info("=" * 70)
        logger.info(f"Source: {source_dir}")
        logger.info(f"Output: {self.output_base}")
        logger.info(f"Pattern: {file_pattern}")
        logger.info(f"Mode: {'COPY' if copy_mode else 'MOVE'}")
        if max_files:
            logger.info(f"Limit: {max_files} files")
        logger.info("=" * 70)

        if not source_dir.exists():
            logger.error(f"Source directory does not exist: {source_dir}")
            return []

        # Find all matching files
        files = sorted(source_dir.glob(file_pattern))

        if max_files:
            files = files[:max_files]

        self.stats["total_files"] = len(files)
        logger.info(f"Found {len(files)} files to process")

        results = []

        for i, filepath in enumerate(files, 1):
            logger.info(f"\n[{i}/{len(files)}] Processing: {filepath.name}")
            result = self.process_file(filepath, copy_mode)
            if result:
                results.append(result)

        # Generate summary
        self._print_summary()

        return results

    def _print_summary(self):
        """Print processing summary"""
        logger.info("\n" + "=" * 70)
        logger.info("ORGANIZATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Files:          {self.stats['total_files']}")
        logger.info(f"Processed:            {self.stats['processed']} [OK]")
        logger.info(f"Skipped (duplicates): {self.stats['skipped']}")
        logger.info(f"Failed:               {self.stats['failed']} [ERROR]")

        if self.stats["processed"] > 0:
            success_rate = (self.stats["processed"] / self.stats["total_files"]) * 100
            logger.info(f"Success Rate:         {success_rate:.1f}%")

            avg_time = sum(self.stats["processing_times"]) / len(self.stats["processing_times"])
            logger.info(f"Avg Processing Time:  {avg_time:.2f}s")
            logger.info(f"Total Time:           {sum(self.stats['processing_times']):.2f}s")

        if self.stats["by_language"]:
            logger.info("\nDocuments by Language:")
            for lang, count in sorted(self.stats["by_language"].items()):
                logger.info(f"  - {lang}: {count}")

        if self.stats["by_topic"]:
            logger.info("\nTop 10 Topics:")
            sorted_topics = sorted(self.stats["by_topic"].items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:10]:
                logger.info(f"  - {topic}: {count}")

        logger.info("=" * 70)

    def export_results(self, results: List[Dict], output_file: Path = Path("organization_results.json")):
        """
        Export results to JSON file.

        Args:
            results: List of processing results
            output_file: Output file path
        """
        export_data = {
            "results": results,
            "statistics": {
                "total_files": self.stats["total_files"],
                "processed": self.stats["processed"],
                "skipped": self.stats["skipped"],
                "failed": self.stats["failed"],
                "by_language": dict(self.stats["by_language"]),
                "by_topic": dict(self.stats["by_topic"]),
                "avg_processing_time": sum(self.stats["processing_times"]) / len(self.stats["processing_times"]) if self.stats["processing_times"] else 0
            }
        }

        output_file.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
        logger.info(f"Results exported to {output_file}")

    def create_index(self):
        """Create an index file showing the organization structure"""
        index_path = self.output_base / "INDEX.md"

        lines = ["# Document Organization Index\n\n"]
        lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        lines.append("## Structure\n\n")

        # Walk through organized directory
        for lang_dir in sorted(self.output_base.iterdir()):
            if lang_dir.is_dir() and lang_dir.name != "INDEX.md":
                lines.append(f"### {lang_dir.name.upper()}\n\n")

                for topic_dir in sorted(lang_dir.iterdir()):
                    if topic_dir.is_dir():
                        files = list(topic_dir.glob("*"))
                        lines.append(f"#### {topic_dir.name} ({len(files)} files)\n\n")

                        for file in sorted(files)[:10]:  # Show max 10 files per topic
                            lines.append(f"- {file.name}\n")

                        if len(files) > 10:
                            lines.append(f"- ... and {len(files) - 10} more\n")

                        lines.append("\n")

        # Add statistics
        lines.append("## Statistics\n\n")
        lines.append(f"- Total processed: {self.stats['processed']}\n")
        lines.append(f"- Languages: {len(self.stats['by_language'])}\n")
        lines.append(f"- Topics: {len(self.stats['by_topic'])}\n")

        index_path.write_text("".join(lines), encoding='utf-8')
        logger.info(f"Index created at {index_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Organize documents by analyzing and categorizing them")
    parser.add_argument("source_dir", type=str, help="Source directory containing documents")
    parser.add_argument("--output", "-o", type=str, default="organized_documents",
                       help="Output directory for organized documents")
    parser.add_argument("--pattern", "-p", type=str, default="*.md",
                       help="File pattern to match (default: *.md)")
    parser.add_argument("--move", "-m", action="store_true",
                       help="Move files instead of copying")
    parser.add_argument("--limit", "-l", type=int,
                       help="Limit number of files to process")

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output)

    logger.info("Initializing Document Organizer...")
    organizer = DocumentOrganizer(output_base=output_dir)

    # Process directory
    results = organizer.process_directory(
        source_dir=source_dir,
        file_pattern=args.pattern,
        copy_mode=not args.move,
        max_files=args.limit
    )

    # Export results
    organizer.export_results(results)

    # Create index
    organizer.create_index()

    # Exit code based on results
    if organizer.stats["failed"] > 0:
        logger.warning(f"{organizer.stats['failed']} file(s) failed processing")
        sys.exit(1)
    else:
        logger.info("All files processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
