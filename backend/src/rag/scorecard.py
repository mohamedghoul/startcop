"""
ReadinessScorecard: Quantifies regulatory compliance readiness for a startup based on RAG pipeline outputs.
- Assigns weights to key regulatory areas (e.g., data privacy, licensing, AML, etc.)
- Calculates overall readiness score and detailed breakdown
- Highlights missing or weak areas
"""
from typing import List, Dict, Any

class ReadinessScorecard:
    """
    Quantifies regulatory compliance readiness for a startup based on RAG pipeline outputs.
    Assigns weights to key regulatory areas, calculates overall readiness score and breakdown, highlights gaps.
    """
    def __init__(self, regulatory_areas: Dict[str, float] = None):
        """
        Initialize ReadinessScorecard.
        Args:
            regulatory_areas (Dict[str, float], optional): Area name to weight (sums to 1.0).
        """
        if regulatory_areas is None:
            regulatory_areas = {
                "data_privacy": 0.3,
                "licensing": 0.2,
                "aml": 0.2,
                "governance": 0.15,
                "reporting": 0.15
            }
        self.regulatory_areas = regulatory_areas

    def score(self, rag_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score the RAG results for regulatory readiness.
        Args:
            rag_results (List[Dict[str, Any]]): Each with 'area', 'compliance', and 'explanation'.
        Returns:
            Dict[str, Any]: Overall score, per-area scores, gaps, and explanations.
        """
        area_scores = {area: 0.0 for area in self.regulatory_areas}
        area_found = {area: False for area in self.regulatory_areas}
        explanations = {area: [] for area in self.regulatory_areas}
        for result in rag_results:
            area = result.get('area')
            compliance = result.get('compliance', 0.0)
            explanation = result.get('explanation', "")
            if area in area_scores:
                area_scores[area] = max(area_scores[area], compliance)
                area_found[area] = True
                explanations[area].append(explanation)
        weighted_score = sum(area_scores[area] * self.regulatory_areas[area] for area in self.regulatory_areas)
        gaps = [area for area, found in area_found.items() if not found or area_scores[area] < 0.5]
        return {
            "overall_score": round(weighted_score * 100, 1),
            "area_scores": area_scores,
            "gaps": gaps,
            "explanations": explanations
        }
