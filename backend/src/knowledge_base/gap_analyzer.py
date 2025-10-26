from sentence_transformers import SentenceTransformer
import chromadb, json, os
from typing import Dict, Any, List
from document_processor.models import Gap, DocumentEntities
import pycountry

class GapAnalyzer:
    def __init__(self, kb_path: str, resource_path: str):
        self.chroma = chromadb.Client(chromadb.Settings(anonymized_telemetry=False))
        self.collection = self.chroma.create_collection("qcb_rules")
        self._load_kb(kb_path)
        with open(resource_path, 'r') as f:
            self.resources = json.load(f)

    def _load_kb(self, kb_path: str):
        kb = json.load(open(kb_path, encoding="utf-8"))
        for cat, rules in kb["regulations"].items():
            for idx, rule in enumerate(rules):      
                self.collection.add(
                    documents=[rule.get("content", "")],
                    metadatas={"article": rule.get("title", ""), "category": cat},
                    ids=f"{cat}_{idx}"               
                )

    # backend/src/knowledge_base/gap_analyzer.py
    def find_gaps(self, entities: DocumentEntities) -> List[Gap]:
        gaps = []

        # 0. Data residency (generic country checker)
        if entities.data_storage and entities.data_storage.get("location"):
            if self._is_outside_qatar(entities.data_storage["location"]):
                gaps.append(Gap(
                    gap_type="DATA_RESIDENCY",
                    risk_level="HIGH",
                    qcb_article="qcb_aml_data_protection_regulation.md:2.1.1",
                    description="Data stored outside Qatar",
                    recommendation=self._pick_expert("EXPERT_C101")
                ))

        # 2. Compliance officer
        if not entities.corporate_structure.compliance_officer:
            gaps.append(Gap(
                gap_type="COMPLIANCE_OFFICER",
                risk_level="HIGH",
                qcb_article="qcb_aml_data_protection_regulation.md:2.2.1",
                description="No dedicated compliance officer",
                recommendation=self._pick_expert("EXPERT_C102")
            ))

        # 3. Capital short-fall
        for m in entities.financial_metrics:
            if m.metric_type in {"capital_requirement", "share_capital"} and m.value < 7_500_000:
                gaps.append(Gap(
                    gap_type="CAPITAL_SHORTFALL",
                    risk_level="HIGH",
                    qcb_article="qcb_fintech_licensing_pathways.md:1.2.2",
                    description=f"Capital QAR {m.value:,} < required 7.5M",
                    recommendation=self._pick_program("QDB_INCUBATOR_001")
                ))

        # 4. AML large volume
        for m in entities.financial_metrics:
            if m.metric_type == "transaction_limit" and m.value > 45_000:
                gaps.append(Gap(
                    gap_type="AML_MONITORING",
                    risk_level="MEDIUM",
                    qcb_article="qcb_aml_data_protection_regulation.md:1.1.2",
                    description="Large volume triggers enhanced CDD",
                    recommendation=self._pick_program("QDB_EXPERT_002")
                ))
        return gaps
    
    
    def _pick_program(self, program_id: str) -> Dict[str, Any]:
        for p in self.resources.get("qdb_programs", []):
            if p["program_id"] == program_id:
                return p
        return {}

    def _pick_expert(self, expert_id: str) -> Dict[str, Any]:
        for e in self.resources.get("compliance_experts", []):
            if e["expert_id"] == expert_id:
                return e
        return {}
    
    def _is_outside_qatar(self, location: str) -> bool:
        """Return True if location string contains any country != Qatar."""
        for country in pycountry.countries:
            if country.name.lower() in location.lower() and country.alpha_2 != "QA":
                return True
        return False