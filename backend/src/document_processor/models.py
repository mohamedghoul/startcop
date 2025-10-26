# src/document_processor/models.py
"""
Data Models for Document Processing
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class BusinessActivity:
    activity_type: str
    description: str
    confidence: float = 0.0
    source_method: str = "unknown"
    revenue_model: Optional[str] = None


@dataclass
class FinancialMetric:
    metric_type: str
    value: float
    currency: str = "QAR"
    description: str = ""
    confidence: float = 0.5


@dataclass
class CorporateStructure:
    entity_type: str = "Unknown"
    board_members: List[str] = field(default_factory=list)
    compliance_officer: Optional[str] = None
    share_capital: Optional["FinancialMetric"] = None
    governance_policies: List[str] = field(default_factory=list)


@dataclass
class ExtractionResult:
    entities: List[Any]
    confidence: float = 0.0
    method_used: str = ""
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class DocumentEntities:
    business_activities: List[BusinessActivity] = field(default_factory=list)
    financial_metrics: List[FinancialMetric] = field(default_factory=list)
    corporate_structure: CorporateStructure = None
    data_storage: Optional[Dict[str, Any]] = None
    compliance_policies: List[str] = field(default_factory=list)


@dataclass
class ProcessingResult:
    document_id: str
    filename: str
    processing_timestamp: datetime = None
    entities: DocumentEntities = None
    confidence_score: float = 0.0
    processing_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Gap:
    """Single regulatory gap / deficiency"""

    gap_type: str = ""  # DATA_RESIDENCY, COMPLIANCE_OFFICER, ...
    risk_level: str = ""  # HIGH, MEDIUM, LOW
    qcb_article: str = ""  # e.g. "qcb_aml_data_protection_regulation.md:2.1.1"
    description: str = ""
    recommendation: Dict[str, Any] = field(
        default_factory=dict
    )  # JSON from resource_mapping_data.json
