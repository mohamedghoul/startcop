"""
ReadinessScorecard: Quantifies regulatory compliance readiness for a startup based on RAG pipeline outputs.
- Assigns weights to key regulatory areas (e.g., data privacy, licensing, AML, etc.)
- Calculates overall readiness score and detailed breakdown
- Highlights missing or weak areas
"""
from typing import List, Dict, Any

class ReadinessScorecard:
    def __init__(self, regulatory_areas: Dict[str, float] = None):
        """
        regulatory_areas: Dict of area name to weight (sums to 1.0)
        Example: {"data_privacy": 0.3, "licensing": 0.2, "aml": 0.2, "governance": 0.15, "reporting": 0.15}
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
        rag_results: List of dicts, each with 'area', 'compliance', and 'explanation'.
        'compliance' is a float between 0 (not covered) and 1 (fully compliant).
        Returns: dict with overall score, per-area scores, and gap analysis.
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
