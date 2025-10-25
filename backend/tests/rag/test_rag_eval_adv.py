"""
Advanced tests for the RAG pipeline.
Covers: adversarial queries, semantic similarity, confidence scoring, and explainability edge cases.
Run with pytest.
"""

import pytest
from ...src.rag.pipeline import RAGPipeline


@pytest.fixture(scope="module")
def rag():
    return RAGPipeline(collection_name="regulations_test")


# 1. Adversarial Query Test
def test_adversarial_query(rag):
    query = "We store all data in Qatar, except for backups in Singapore."
    results = rag.retrieve(query, top_k=3)
    explanation = rag.generate(query, results)
    assert (
        any("Data Residency" in chunk["text"] for chunk in results)
        or "Qatar" in explanation
    )


# 2. Semantic Similarity Test
def test_semantic_similarity(rag):
    query = "Our customer information is kept on servers outside the country."
    results = rag.retrieve(query, top_k=3)
    assert any("Data Residency" in chunk["text"] for chunk in results)


# 3. Confidence Scoring Test (if implemented)
def test_confidence_scoring(rag):
    query = "We have a compliance officer."
    results = rag.retrieve(query, top_k=3)
    if results and "distance" in results[0]:
        for chunk in results:
            assert 0.0 <= chunk["distance"] <= 2.0


# 4. Explainability Edge Case: Contradictory Info
def test_contradictory_query(rag):
    query = "We have a compliance officer, but we do not have a compliance officer."
    results = rag.retrieve(query, top_k=3)
    explanation = rag.generate(query, results)
    assert "compliance officer" in explanation.lower()


# 5. Large Batch Test
def test_large_batch(rag):
    queries = [f"Test query {i}" for i in range(50)]
    for query in queries:
        results = rag.retrieve(query, top_k=2)
        assert isinstance(results, list)
