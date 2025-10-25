"""
Test ReadinessScorecard logic for regulatory compliance scoring.
"""

import pytest
from ...src.rag.scorecard import ReadinessScorecard


def test_scorecard_basic():
    scorecard = ReadinessScorecard()
    rag_results = [
        {
            "area": "data_privacy",
            "compliance": 1.0,
            "explanation": "All privacy requirements met.",
        },
        {
            "area": "licensing",
            "compliance": 0.8,
            "explanation": "Most licenses obtained.",
        },
        {
            "area": "aml",
            "compliance": 0.5,
            "explanation": "Basic AML controls in place.",
        },
        {
            "area": "governance",
            "compliance": 0.0,
            "explanation": "No governance policy.",
        },
        {
            "area": "reporting",
            "compliance": 0.6,
            "explanation": "Some reporting processes exist.",
        },
    ]
    result = scorecard.score(rag_results)
    assert 0 <= result["overall_score"] <= 100
    assert "gaps" in result
    assert "governance" in result["gaps"]
    assert result["area_scores"]["data_privacy"] == 1.0
    assert result["area_scores"]["governance"] == 0.0
    assert result["area_scores"]["aml"] == 0.5
    assert result["area_scores"]["licensing"] == 0.8
    assert result["area_scores"]["reporting"] == 0.6


def test_scorecard_missing_areas():
    scorecard = ReadinessScorecard()
    rag_results = [
        {"area": "data_privacy", "compliance": 0.9, "explanation": "Strong privacy."},
        {"area": "licensing", "compliance": 0.7, "explanation": "Partial licensing."},
    ]
    result = scorecard.score(rag_results)
    assert "aml" in result["gaps"]
    assert "governance" in result["gaps"]
    assert "reporting" in result["gaps"]
    assert result["area_scores"]["aml"] == 0.0
    assert result["area_scores"]["governance"] == 0.0
    assert result["area_scores"]["reporting"] == 0.0


def test_scorecard_all_compliant():
    scorecard = ReadinessScorecard()
    rag_results = [
        {"area": area, "compliance": 1.0, "explanation": "Compliant."}
        for area in scorecard.regulatory_areas
    ]
    result = scorecard.score(rag_results)
    assert result["overall_score"] == 100.0
    assert result["gaps"] == []
    for area in scorecard.regulatory_areas:
        assert result["area_scores"][area] == 1.0
