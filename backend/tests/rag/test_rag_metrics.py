"""
Extended tests and metric logging for the RAG pipeline.
Logs precision, recall, and F1 for all test cases, and covers more edge cases.
Run with pytest.
"""

import pytest
from src.rag.pipeline import RAGPipeline
from collections import defaultdict


@pytest.fixture(scope="module")
def rag():
    return RAGPipeline(collection_name="regulations_test")


# Helper for metric logging
metrics = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "total": 0})


def log_metrics(test_name, expected, results, label):
    found = any(expected in chunk["text"] for chunk in results)
    metrics[test_name]["total"] += 1
    if found:
        metrics[test_name]["tp"] += 1
    else:
        metrics[test_name]["fn"] += 1
    for chunk in results:
        if expected in chunk["text"]:
            metrics[test_name]["tp"] += 1
        else:
            metrics[test_name]["fp"] += 1


# 1. Extended Precision/Recall/F1 Evaluation
def test_precision_recall_f1(rag):
    test_cases = [
        ("Our data is stored on AWS in Ireland and Singapore.", "Data Residency"),
        ("We do not have a dedicated Compliance Officer.", "Compliance Officer"),
        ("Our paid-up capital is QAR 5,000,000.", "Marketplace Lending"),
        ("We process cross-border transactions up to QAR 45,000.", "Source of Funds"),
        ("We have a Board of Directors.", "Board of Directors"),
        ("We use 256-bit encryption for all data.", "Data Protection"),
        ("We have an annual external audit.", "Annual Audit"),
        ("We collect two forms of ID for KYC.", "KYC Documentation"),
    ]
    top_k = 3
    for query, expected in test_cases:
        results = rag.retrieve(query, top_k=top_k)
        log_metrics("precision_recall_f1", expected, results, label=query)
    m = metrics["precision_recall_f1"]
    precision = m["tp"] / (m["tp"] + m["fp"] + 1e-8)
    recall = m["tp"] / (m["tp"] + m["fn"] + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}")
    assert recall >= 0.7, "Recall should be at least 70% for extended cases."
    assert precision >= 0.7, "Precision should be at least 70% for extended cases."


# 2. Edge Case: Empty Query
def test_empty_query(rag):
    query = ""
    results = rag.retrieve(query, top_k=3)
    explanation = rag.generate(query, results)
    assert len(results) == 0 or "No relevant regulations found" in explanation


# 3. Edge Case: Very Long Query
def test_very_long_query(rag):
    query = "We are a fintech company. " * 100
    results = rag.retrieve(query, top_k=3)
    assert isinstance(results, list)


# 4. Explanation Quality: All Results Referenced
def test_explanation_references_all(rag):
    query = "We have an annual external audit and a Board of Directors."
    results = rag.retrieve(query, top_k=5)
    explanation = rag.generate(query, results)
    for chunk in results:
        assert chunk["text"] in explanation


# 5. Metric Logging Output
def test_print_metrics():
    print("\n--- RAG Pipeline Test Metrics ---")
    for test_name, m in metrics.items():
        precision = m["tp"] / (m["tp"] + m["fp"] + 1e-8)
        recall = m["tp"] / (m["tp"] + m["fn"] + 1e-8)
        f1 = 2 * precision * recall / (precision + recall + 1e-8)
        print(
            f"{test_name}: Precision={precision:.2f}, Recall={recall:.2f}, F1={f1:.2f}"
        )
