"""
Unit/integration tests for the RAG pipeline using pytest.
These tests validate retrieval and explanation accuracy using mock data and gap analysis examples.
"""

import pytest
from src.rag.pipeline import RAGPipeline


@pytest.fixture(scope="module")
def rag():
    # Use the test collection for isolation
    return RAGPipeline(collection_name="regulations_test")


def test_data_residency_retrieval(rag):
    query = "Our data is stored on AWS in Ireland and Singapore."
    results = rag.retrieve(query, top_k=3)
    import logging
    from src.rag.pipeline import RAGPipeline

    @pytest.fixture(scope="module")
    def rag_pipeline():
        # Use the test collection for isolation
        return RAGPipeline(collection_name="regulations_test")
    query = "We do not have a dedicated Compliance Officer."
    results = rag.retrieve(query, top_k=3)
    assert any(
        "Compliance Officer" in chunk["text"] or "2.2.1" in chunk["text"]
        for chunk in results
    ), "Should retrieve Compliance Officer regulation."


def test_capital_requirement_gap(rag):
    query = "Our paid-up capital is QAR 5,000,000."
    results = rag.retrieve(query, top_k=3)
    assert any(
        "Marketplace Lending" in chunk["text"] or "1.2.2" in chunk["text"]
        for chunk in results
    ), "Should retrieve Marketplace Lending capital requirement."


def test_explanation_contains_regulation(rag):
    query = "Our data is stored on AWS in Ireland and Singapore."
    results = rag.retrieve(query, top_k=3)
    explanation = rag.generate(query, results)
    assert (
        "Data Residency" in explanation or "2.1.1" in explanation
    ), "Explanation should mention Data Residency regulation."
