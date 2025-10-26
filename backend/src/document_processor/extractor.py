# src/document_processor/extractor.py
"""
Main Document Intelligence Engine
Unified, clean architecture with state-of-the-art models
"""

import hashlib
import os
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path
import re

from .parser import DocumentParser
from .activity_extractor import BusinessActivityExtractor
from .financial_extractor import FinancialExtractor
from .corporate_extractor import CorporateExtractor
from .models import ProcessingResult, DocumentEntities, CorporateStructure  # Fixed import
from .config import MODEL_SETTINGS, BUSINESS_ACTIVITIES, FINANCIAL_PATTERNS  # Added imports

logger = logging.getLogger(__name__)

class DocumentIntelligenceEngine:
    """
    Main document processing engine that coordinates all extractors
    Uses best-in-class models for maximum accuracy
    """
    
    def __init__(self, device: str = "auto"):
        """
        Initialize with state-of-the-art models
        
        Args:
            device: 'auto', 'cuda', or 'cpu'
        """
        self.device = device
        self.parser = DocumentParser()
        
        # Initialize specialized extractors with advanced models
        self.activity_extractor = BusinessActivityExtractor()
        self.financial_extractor = FinancialExtractor()
        self.corporate_extractor = CorporateExtractor()
        
        logger.info(f"Document Intelligence Engine initialized on {device}")
    
    def process_document(self, file_path: str, document_id: Optional[str] = None) -> ProcessingResult:
        """Process document file"""
        try:
            if not document_id:
                document_id = self._generate_document_id(file_path)
            
            filename = os.path.basename(file_path)
            logger.info(f"Processing: {filename}")
            
            # Extract text
            text = self.parser.parse_document(file_path)
            
            # Process text
            return self.process_text(text, document_id, filename)
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
    
    def process_text(self, text: str, document_id: str, filename: str = "text_input") -> ProcessingResult:
        """Process raw text"""
        try:
            if not text.strip():
                raise ValueError("Empty text provided")
            
            start_time = datetime.now()
            
            # Run all extractors (parallel processing ready)
            activity_result = self.activity_extractor.process_with_error_handling(text)
            financial_result = self.financial_extractor.process_with_error_handling(text)
            corporate_result = self.corporate_extractor.process_with_error_handling(text)
            
            # Build result
            result = self._build_result(
                activity_result, financial_result, corporate_result,
                document_id, filename, start_time, text
            )
            
            logger.info(f"Processing complete. Confidence: {result.confidence_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            raise
    
    def _build_result(self, activity_result, financial_result, corporate_result,
                      document_id: str, filename: str, start_time: datetime, text: str) -> ProcessingResult:
        """Build final result from extractor outputs"""
        
        # Extract corporate structure from result
        corporate_structure = (corporate_result.entities[0] 
                             if corporate_result.entities 
                             else CorporateStructure())
        
        # Create entities
        entities = DocumentEntities(
            business_activities=activity_result.entities,
            financial_metrics=financial_result.entities,
            corporate_structure=corporate_structure,
            data_storage=self._extract_data_storage(text),
            compliance_policies=self._extract_compliance_policies(text)
        )
        
        # Calculate overall confidence
        overall_confidence = self._calculate_confidence(
            activity_result.confidence,
            financial_result.confidence, 
            corporate_result.confidence
        )
        
        # Collect errors
        all_errors = (
            activity_result.errors + 
            financial_result.errors + 
            corporate_result.errors
        )
        
        return ProcessingResult(
            document_id=document_id,
            filename=filename,
            processing_timestamp=datetime.now(),
            entities=entities,
            confidence_score=overall_confidence,
            processing_errors=all_errors,
            metadata={
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'extractors_used': ['activity', 'financial', 'corporate'],
                'text_length': len(text)
            }
        )
    
    def _calculate_confidence(self, activity_conf: float, financial_conf: float, 
                            corporate_conf: float) -> float:
        """Calculate weighted overall confidence"""
        weights = [0.4, 0.35, 0.25]  # activities, financial, corporate
        confidences = [activity_conf, financial_conf, corporate_conf]
        
        # Only include non-zero confidences
        valid = [(conf, weight) for conf, weight in zip(confidences, weights) if conf > 0]
        
        if not valid:
            return 0.0
        
        total_weight = sum(weight for _, weight in valid)
        weighted_sum = sum(conf * weight for conf, weight in valid)
        
        return weighted_sum / total_weight
    
    def _extract_data_storage(self, text: str) -> Optional[dict]:
        storage = {}

        # 1. Cloud provider
        for provider, pat in {'aws': r'aws', 'azure': r'azure', 'gcp': r'google cloud'}.items():
            if re.search(pat, text, re.IGNORECASE):
                storage['provider'] = provider
                break

        # 2. Location – capture whole phrase  (“AWS regions in Ireland and Singapore”)
        loc_match = re.search(
            r'(?:hosted|stored|located)\s+(?:in|on|across)\s+([^\n,.]+)', text, re.I
        )
        if loc_match:
            storage['location'] = loc_match.group(1).strip()

        return storage if storage else None
    
    def _extract_compliance_policies(self, text: str) -> list:
        """Extract mentioned compliance policies"""
        policies = []
        
        policy_map = {
            'aml_policy': r'anti.money laundering|aml',
            'kyc_policy': r'know your customer|kyc',
            'data_privacy': r'data privacy|data protection'
        }
        
        for policy_type, pattern in policy_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                policies.append(policy_type)
        
        return policies
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate unique document ID"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"doc_{timestamp}_{file_hash[:8]}"
        except Exception:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"doc_{timestamp}"