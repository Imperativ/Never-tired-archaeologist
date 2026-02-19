"""
Batch testing script for Never-Tired-Archaeologist

Tests the pipeline with multiple sample documents to validate robustness.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict
import time

from src.database import DocDatabase
from src.embedder import LocalEmbedder
from src.llm import Analyzer
from src.models import DocumentMetadata


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BatchTester:
    """Batch testing utility for document processing pipeline"""

    def __init__(self):
        self.db = DocDatabase()
        self.embedder = LocalEmbedder()
        self.analyzer = Analyzer()
        self.results: List[Dict] = []

    def create_test_documents(self, output_dir: Path = Path("test_documents")):
        """
        Create a set of diverse test documents.

        Args:
            output_dir: Directory to store test documents
        """
        output_dir.mkdir(exist_ok=True)
        logger.info(f"Creating test documents in {output_dir}")

        test_docs = {
            "test_01_short_english.txt": """Machine Learning Overview

Machine learning is a subset of artificial intelligence that enables systems to learn from data.
It includes supervised learning, unsupervised learning, and reinforcement learning approaches.""",

            "test_02_long_german.txt": """Quantencomputing: Die Zukunft der Informationsverarbeitung

Quantencomputer nutzen die Prinzipien der Quantenmechanik, um Berechnungen durchzuführen, die für klassische Computer praktisch unmöglich sind. Im Gegensatz zu klassischen Bits, die entweder 0 oder 1 sein können, verwenden Quantencomputer Qubits, die durch Superposition gleichzeitig in mehreren Zuständen existieren können.

Die wichtigsten Quantenalgorithmen wie Shor's Algorithmus für Faktorisierung und Grover's Algorithmus für Datenbanksuche zeigen exponentielles Speedup gegenüber klassischen Ansätzen. Unternehmen wie IBM, Google und IonQ entwickeln aktuell NISQ-Geräte (Noisy Intermediate-Scale Quantum), die bereits heute für bestimmte Anwendungen eingesetzt werden können.

Herausforderungen bleiben die Fehlerkorrektur und die Skalierung auf tausende fehlertolerante Qubits.""",

            "test_03_technical_code.txt": """# REST API Design Best Practices

## 1. Use HTTP Methods Correctly
- GET: Retrieve resources
- POST: Create new resources
- PUT: Update entire resources
- PATCH: Partial updates
- DELETE: Remove resources

## 2. Resource Naming
Use nouns, not verbs:
- Good: /api/users, /api/orders
- Bad: /api/getUsers, /api/createOrder

## 3. Status Codes
- 200 OK: Success
- 201 Created: Resource created
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Server error

## 4. Versioning
Include version in URL: /api/v1/users""",

            "test_04_multilingual.txt": """Artificial Intelligence - L'Intelligence Artificielle - Künstliche Intelligenz

English: AI is transforming industries worldwide through automation and data analysis.
Français: L'IA transforme les industries du monde entier grâce à l'automatisation et à l'analyse des données.
Deutsch: KI verändert Branchen weltweit durch Automatisierung und Datenanalyse.

Key concepts: Machine Learning, Deep Learning, Neural Networks, NLP
Concepts clés: Apprentissage automatique, Apprentissage profond, Réseaux de neurones, TAL
Schlüsselkonzepte: Maschinelles Lernen, Deep Learning, Neuronale Netze, NLP""",

            "test_05_scientific.txt": """CRISPR-Cas9 Gene Editing Technology

Abstract:
CRISPR-Cas9 (Clustered Regularly Interspaced Short Palindromic Repeats) is a revolutionary gene-editing tool that allows precise modification of DNA sequences in living organisms.

Mechanism:
The Cas9 protein acts as molecular scissors, guided by RNA to specific DNA locations. Upon binding, Cas9 creates double-strand breaks, triggering cellular repair mechanisms that can be exploited to insert, delete, or modify genes.

Applications:
- Disease treatment (sickle cell anemia, cancer immunotherapy)
- Agricultural improvements (drought-resistant crops)
- Biotechnology (engineered microorganisms)

Ethical considerations include germline editing and potential off-target effects.""",

            "test_06_short_list.txt": """Shopping List:
- Milk
- Bread
- Eggs
- Butter
- Coffee""",

            "test_07_special_chars.txt": """Unicode Test Document 🚀

This document contains special characters:
• Bullet points
→ Arrows
© Copyright symbols
€ Currency symbols
α β γ Greek letters
中文 Chinese characters
العربية Arabic text
emoji: 😀 🎉 ✅ ⚠️ 🔧

Mathematical notation: ∑ ∫ √ ∞ ≈ ≠
""",
        }

        created_count = 0
        for filename, content in test_docs.items():
            filepath = output_dir / filename
            filepath.write_text(content, encoding='utf-8')
            created_count += 1
            logger.info(f"Created: {filename}")

        logger.info(f"Successfully created {created_count} test documents")
        return list(test_docs.keys())

    def process_document(self, filepath: Path) -> Dict:
        """
        Process a single document and return results.

        Args:
            filepath: Path to document

        Returns:
            Dictionary with processing results
        """
        result = {
            "filename": filepath.name,
            "success": False,
            "error": None,
            "metadata": None,
            "processing_time": 0.0,
            "content_length": 0,
            "embedding_dim": 0
        }

        start_time = time.time()

        try:
            # Read file
            content = filepath.read_text(encoding='utf-8')
            result["content_length"] = len(content)

            # Check for duplicates
            content_hash = self.db._compute_hash(content)
            if self.db.document_exists(content_hash):
                result["error"] = "Duplicate (already in database)"
                result["processing_time"] = time.time() - start_time
                return result

            # Generate embedding
            embedding = self.embedder.generate_embedding(content)
            result["embedding_dim"] = len(embedding)

            # Analyze with Claude
            metadata = self.analyzer.analyze_text(content)
            result["metadata"] = metadata.model_dump()

            # Store in database
            doc_id = self.db.add_document(content, metadata, embedding)

            result["success"] = True
            result["doc_id"] = doc_id
            result["processing_time"] = time.time() - start_time

            logger.info(f"[OK] {filepath.name} processed successfully in {result['processing_time']:.2f}s")

        except Exception as e:
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            logger.error(f"[ERROR] {filepath.name} failed: {e}")

        return result

    def run_batch_test(self, test_dir: Path = Path("test_documents")) -> Dict:
        """
        Run batch test on all documents in test directory.

        Args:
            test_dir: Directory containing test documents

        Returns:
            Summary statistics
        """
        logger.info("=" * 60)
        logger.info("BATCH TEST STARTED")
        logger.info("=" * 60)

        if not test_dir.exists():
            logger.warning(f"Test directory {test_dir} not found. Creating test documents...")
            self.create_test_documents(test_dir)

        # Get all .txt files
        test_files = sorted(test_dir.glob("*.txt"))
        logger.info(f"Found {len(test_files)} test documents")

        # Process each document
        for filepath in test_files:
            result = self.process_document(filepath)
            self.results.append(result)

        # Generate summary
        summary = self._generate_summary()
        self._print_summary(summary)

        logger.info("=" * 60)
        logger.info("BATCH TEST COMPLETED")
        logger.info("=" * 60)

        return summary

    def _generate_summary(self) -> Dict:
        """Generate summary statistics from results"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total - successful

        total_time = sum(r["processing_time"] for r in self.results)
        avg_time = total_time / total if total > 0 else 0

        avg_length = sum(r["content_length"] for r in self.results) / total if total > 0 else 0

        errors = {}
        for r in self.results:
            if r["error"]:
                errors[r["filename"]] = r["error"]

        return {
            "total_documents": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "total_processing_time": total_time,
            "avg_processing_time": avg_time,
            "avg_content_length": avg_length,
            "errors": errors
        }

    def _print_summary(self, summary: Dict):
        """Print formatted summary"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("BATCH TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Documents:      {summary['total_documents']}")
        logger.info(f"Successful:           {summary['successful']} [OK]")
        logger.info(f"Failed:               {summary['failed']} [FAIL]")
        logger.info(f"Success Rate:         {summary['success_rate']:.1f}%")
        logger.info(f"Total Processing Time: {summary['total_processing_time']:.2f}s")
        logger.info(f"Avg Processing Time:  {summary['avg_processing_time']:.2f}s")
        logger.info(f"Avg Content Length:   {summary['avg_content_length']:.0f} chars")

        if summary['errors']:
            logger.info("")
            logger.info("Errors:")
            for filename, error in summary['errors'].items():
                logger.info(f"  - {filename}: {error}")

        logger.info("=" * 60)

    def export_results(self, output_file: Path = Path("batch_test_results.json")):
        """Export results to JSON file"""
        import json

        export_data = {
            "results": self.results,
            "summary": self._generate_summary()
        }

        output_file.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
        logger.info(f"Results exported to {output_file}")


def main():
    """Main entry point"""
    logger.info("Initializing Batch Tester...")

    tester = BatchTester()

    # Create test documents if they don't exist
    test_dir = Path("test_documents")
    if not test_dir.exists() or len(list(test_dir.glob("*.txt"))) == 0:
        logger.info("Creating test documents...")
        tester.create_test_documents()

    # Run batch test
    summary = tester.run_batch_test()

    # Export results
    tester.export_results()

    # Exit with appropriate code
    if summary["failed"] > 0:
        logger.warning(f"{summary['failed']} document(s) failed processing")
        sys.exit(1)
    else:
        logger.info("All documents processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
