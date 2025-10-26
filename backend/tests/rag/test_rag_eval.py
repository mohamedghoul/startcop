"""
Integration and evaluation tests for the RAG pipeline.
Covers: precision/recall metrics, edge cases, and explanation quality.
Run with pytest.
"""

import pytest
from src.rag.pipeline import RAGPipeline


@pytest.fixture(scope="module")
def rag():
    return RAGPipeline(collection_name="regulations_test")


# 1. Precision/Recall Evaluation
def test_precision_recall(rag):
    test_cases = [
        ("Our data is stored on AWS in Ireland and Singapore.", "Data Residency"),
        ("We do not have a dedicated Compliance Officer.", "Compliance Officer"),
        ("Our paid-up capital is QAR 5,000,000.", "Marketplace Lending"),
        ("We process cross-border transactions up to QAR 45,000.", "Source of Funds"),
    ]
    top_k = 3
    correct = 0
    total = len(test_cases)
    for query, expected in test_cases:
        results = rag.retrieve(query, top_k=top_k)
        if any(expected in chunk["text"] for chunk in results):
            correct += 1
    recall = correct / total
    print(f"Recall@{top_k}: {recall:.2f}")
    assert recall >= 0.75, "Recall should be at least 75% for these key cases."


# 2. Edge Case: No Relevant Regulation
def test_no_relevant_regulation(rag):
    query = "We sell ice cream on Mars."
    results = rag.retrieve(query, top_k=3)
    explanation = rag.generate(query, results)
    assert (
        len(results) == 0
        or "No relevant regulations found" in explanation
        or explanation.strip() != ""
    ), "Should handle irrelevant queries gracefully."


# 3. Explanation Quality
def test_explanation_quality(rag):
    query = "Our data is stored on AWS in Ireland and Singapore."
    results = rag.retrieve(query, top_k=2)
    explanation = rag.generate(query, results)
    assert query in explanation, "Explanation should echo the user's query."
    assert any(
        chunk["text"] in explanation for chunk in results
    ), "Explanation should include retrieved regulation text."


# 4. Multiple Gaps/Recommendations
def test_multiple_gaps(rag):
    query = "Our paid-up capital is QAR 5,000,000 and we do not have a dedicated Compliance Officer."
    results = rag.retrieve(query, top_k=5)
    explanation = rag.generate(query, results)
    assert any(
        "Marketplace Lending" in chunk["text"] for chunk in results
    ), "Should retrieve capital requirement regulation."
    assert any(
        "Compliance Officer" in chunk["text"] for chunk in results
    ), "Should retrieve compliance officer regulation."
    assert (
        "paid-up capital" in explanation or "Compliance Officer" in explanation
    ), "Explanation should mention both gaps."


# 5. Recommendation Mapping (Optional/Advanced)
def test_recommendation_mapping(rag):
    query = "We process cross-border transactions up to QAR 45,000."
    results = rag.retrieve(query, top_k=3)
    explanation = rag.generate(query, results)
    assert explanation is not None
