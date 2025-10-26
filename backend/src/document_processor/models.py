# src/document_processor/models.py
"""
Data Models for Document Processing
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class BusinessActivity(BaseModel):
    """Business activity with confidence scoring"""
    activity_type: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_method: str = "unknown"
    revenue_model: Optional[str] = None

class FinancialMetric(BaseModel):
    """Financial metric"""
    metric_type: str
    value: float
    currency: str = "QAR"
    description: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

class CorporateStructure(BaseModel):
    """Corporate structure"""
    entity_type: str = "Unknown"
    board_members: List[str] = []
    compliance_officer: Optional[str] = None
    share_capital: Optional[FinancialMetric] = None
    governance_policies: List[str] = []

class ExtractionResult(BaseModel):
    """Result from extraction process"""
    entities: List[Any]  # This is the missing class!
    confidence: float
    method_used: str
    processing_time: float
    errors: List[str] = []

class DocumentEntities(BaseModel):
    """All extracted entities"""
    business_activities: List[BusinessActivity]
    financial_metrics: List[FinancialMetric]
    corporate_structure: CorporateStructure
    data_storage: Optional[Dict[str, Any]] = None
    compliance_policies: List[str] = []

class ProcessingResult(BaseModel):
    """Complete processing result"""
    document_id: str
    filename: str
    processing_timestamp: datetime
    entities: DocumentEntities
    confidence_score: float
    processing_errors: List[str] = []
    metadata: Dict[str, Any] = {}


class Gap(BaseModel):
    """Single regulatory gap / deficiency"""
    gap_type: str                           # DATA_RESIDENCY, COMPLIANCE_OFFICER, ...
    risk_level: str                         # HIGH, MEDIUM, LOW
    qcb_article: str                        # e.g. "qcb_aml_data_protection_regulation.md:2.1.1"
    description: str
    recommendation: Dict[str, Any] = {}     # JSON from resource_mapping_data.json    