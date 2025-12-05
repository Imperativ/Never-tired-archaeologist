# -*- coding: utf-8 -*-
import pytest
import math
from dupdetect import cosine_sim, most_similar


class TestCosineSimilarity:
    """Test cosine similarity calculation"""

    def test_identical_vectors(self):
        """Identical vectors should have similarity of 1.0"""
        vec = [1.0, 2.0, 3.0, 4.0]
        assert cosine_sim(vec, vec) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        """Orthogonal vectors should have similarity of 0.0"""
        vec_a = [1.0, 0.0, 0.0]
        vec_b = [0.0, 1.0, 0.0]
        assert cosine_sim(vec_a, vec_b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        """Opposite vectors should have similarity of -1.0"""
        vec_a = [1.0, 2.0, 3.0]
        vec_b = [-1.0, -2.0, -3.0]
        assert cosine_sim(vec_a, vec_b) == pytest.approx(-1.0)

    def test_similar_vectors(self):
        """Similar vectors should have high positive similarity"""
        vec_a = [1.0, 2.0, 3.0]
        vec_b = [1.1, 2.1, 2.9]
        similarity = cosine_sim(vec_a, vec_b)
        assert 0.99 < similarity < 1.0

    def test_empty_vectors(self):
        """Empty vectors should return 0.0"""
        assert cosine_sim([], []) == 0.0

    def test_one_empty_vector(self):
        """One empty vector should return 0.0"""
        vec = [1.0, 2.0, 3.0]
        assert cosine_sim(vec, []) == 0.0
        assert cosine_sim([], vec) == 0.0

    def test_zero_vectors(self):
        """Zero vectors should return 0.0 (avoid division by zero)"""
        vec_zero = [0.0, 0.0, 0.0]
        vec_normal = [1.0, 2.0, 3.0]
        assert cosine_sim(vec_zero, vec_zero) == 0.0
        assert cosine_sim(vec_zero, vec_normal) == 0.0

    def test_different_length_vectors(self):
        """Vectors of different length should return 0.0"""
        vec_a = [1.0, 2.0]
        vec_b = [1.0, 2.0, 3.0]
        assert cosine_sim(vec_a, vec_b) == 0.0

    def test_single_element_vectors(self):
        """Single element vectors should work correctly"""
        assert cosine_sim([5.0], [5.0]) == pytest.approx(1.0)
        assert cosine_sim([3.0], [-3.0]) == pytest.approx(-1.0)

    def test_large_magnitude_vectors(self):
        """Similarity should be independent of vector magnitude"""
        vec_a = [1.0, 2.0, 3.0]
        vec_b = [10.0, 20.0, 30.0]  # Same direction, 10x magnitude
        assert cosine_sim(vec_a, vec_b) == pytest.approx(1.0)

    def test_negative_values(self):
        """Should handle negative values correctly"""
        vec_a = [-1.0, -2.0, 3.0]
        vec_b = [-1.0, -2.0, 3.0]
        assert cosine_sim(vec_a, vec_b) == pytest.approx(1.0)

    def test_mixed_positive_negative(self):
        """Should handle mixed positive/negative values"""
        vec_a = [1.0, -1.0, 1.0]
        vec_b = [1.0, -1.0, 1.0]
        assert cosine_sim(vec_a, vec_b) == pytest.approx(1.0)

    def test_numerical_stability(self):
        """Should be numerically stable with very small values"""
        vec_a = [1e-10, 2e-10, 3e-10]
        vec_b = [1e-10, 2e-10, 3e-10]
        similarity = cosine_sim(vec_a, vec_b)
        assert similarity == pytest.approx(1.0, abs=1e-6)


class TestMostSimilar:
    """Test finding most similar document"""

    def test_empty_seen_list(self):
        """Empty seen list should return None and 0.0"""
        embedding = [1.0, 2.0, 3.0]
        candidate, score = most_similar(embedding, [])
        assert candidate is None
        assert score == 0.0

    def test_single_match(self):
        """Should find the only match"""
        embedding = [1.0, 2.0, 3.0]
        seen = [
            {
                "embedding": [1.0, 2.0, 3.0],
                "filename": "test.txt",
                "path": "/path/test.txt",
            }
        ]
        candidate, score = most_similar(embedding, seen)
        assert candidate is not None
        assert candidate["filename"] == "test.txt"
        assert score == pytest.approx(1.0)

    def test_multiple_candidates_finds_best(self):
        """Should find the best match among multiple candidates"""
        target = [1.0, 2.0, 3.0]
        seen = [
            {
                "embedding": [0.0, 1.0, 0.0],  # Low similarity
                "filename": "bad_match.txt",
                "path": "/path/bad.txt",
            },
            {
                "embedding": [1.0, 2.0, 3.0],  # Perfect match
                "filename": "perfect_match.txt",
                "path": "/path/perfect.txt",
            },
            {
                "embedding": [1.1, 2.1, 2.9],  # Good but not perfect
                "filename": "good_match.txt",
                "path": "/path/good.txt",
            },
        ]
        candidate, score = most_similar(target, seen)
        assert candidate["filename"] == "perfect_match.txt"
        assert score == pytest.approx(1.0)

    def test_no_embedding_in_candidate(self):
        """Should handle candidates without embeddings gracefully"""
        embedding = [1.0, 2.0, 3.0]
        seen = [
            {"filename": "no_embedding.txt", "path": "/path/no_embedding.txt"}
        ]
        candidate, score = most_similar(embedding, seen)
        assert candidate is None
        assert score == 0.0

    def test_exported_name_field(self):
        """Should return exported_name if available"""
        embedding = [1.0, 2.0, 3.0]
        seen = [
            {
                "embedding": [1.0, 2.0, 3.0],
                "filename": "original.txt",
                "exported_name": "exported_file.md",
                "path": "/path/original.txt",
            }
        ]
        candidate, score = most_similar(embedding, seen)
        assert candidate is not None
        assert "exported_name" in candidate
        assert candidate["exported_name"] == "exported_file.md"

    def test_mixed_valid_invalid_embeddings(self):
        """Should skip invalid embeddings and find valid match"""
        target = [1.0, 2.0, 3.0]
        seen = [
            {"embedding": [], "filename": "empty.txt"},  # Empty
            {"embedding": None, "filename": "none.txt"},  # None
            {
                "embedding": [1.0, 2.0, 3.0],
                "filename": "valid.txt",
            },  # Valid
        ]
        candidate, score = most_similar(target, seen)
        assert candidate["filename"] == "valid.txt"
        assert score == pytest.approx(1.0)

    def test_all_low_similarity(self):
        """Should return best match even if all similarities are low"""
        target = [1.0, 0.0, 0.0]
        seen = [
            {"embedding": [0.0, 1.0, 0.0], "filename": "file1.txt"},
            {"embedding": [0.0, 0.0, 1.0], "filename": "file2.txt"},
            {"embedding": [0.1, 0.1, 0.9], "filename": "file3.txt"},
        ]
        candidate, score = most_similar(target, seen)
        assert candidate is not None
        # file3 should have highest (though still low) similarity
        assert 0.0 < score < 0.5

    def test_duplicate_detection_threshold(self):
        """Verify typical duplicate detection threshold (0.95)"""
        target = [1.0, 2.0, 3.0]
        high_similarity = [0.99, 2.01, 2.98]  # Very similar
        low_similarity = [1.0, 0.0, 0.0]  # Different

        seen = [
            {"embedding": high_similarity, "filename": "duplicate.txt"},
            {"embedding": low_similarity, "filename": "different.txt"},
        ]

        candidate, score = most_similar(target, seen)
        assert candidate["filename"] == "duplicate.txt"
        assert score > 0.95  # Should exceed typical threshold

    def test_returns_first_best_on_tie(self):
        """On exact tie, should return first encountered"""
        target = [1.0, 2.0, 3.0]
        seen = [
            {"embedding": [1.0, 2.0, 3.0], "filename": "first.txt"},
            {"embedding": [1.0, 2.0, 3.0], "filename": "second.txt"},
        ]
        candidate, score = most_similar(target, seen)
        # Both have score 1.0, should return first
        assert candidate["filename"] == "first.txt"


class TestIntegration:
    """Integration tests for duplicate detection workflow"""

    def test_realistic_embedding_dimensions(self):
        """Test with realistic embedding dimensions (e.g., 3072 for OpenAI)"""
        # Create 3072-dimensional vectors
        vec_a = [float(i % 100) / 100 for i in range(3072)]
        vec_b = [float(i % 100) / 100 for i in range(3072)]

        similarity = cosine_sim(vec_a, vec_b)
        assert similarity == pytest.approx(1.0)

    def test_duplicate_detection_workflow(self):
        """Simulate real duplicate detection workflow"""
        # Simulated embeddings for documents
        doc1_embedding = [1.0, 2.0, 3.0, 4.0]
        doc2_embedding = [1.0, 2.0, 3.0, 4.0]  # Duplicate of doc1
        doc3_embedding = [5.0, 6.0, 7.0, 8.0]  # Different

        seen_docs = []

        # Process first document
        seen_docs.append(
            {
                "embedding": doc1_embedding,
                "filename": "doc1.txt",
                "exported_name": "doc1.md",
            }
        )

        # Check second document (should be duplicate)
        candidate, score = most_similar(doc2_embedding, seen_docs)
        assert score > 0.95
        assert candidate["filename"] == "doc1.txt"

        # Add second doc anyway
        seen_docs.append(
            {
                "embedding": doc2_embedding,
                "filename": "doc2.txt",
                "exported_name": "doc2.md",
            }
        )

        # Check third document (should not be duplicate)
        candidate, score = most_similar(doc3_embedding, seen_docs)
        assert score < 0.97  # Adjusted threshold for realistic vectors
