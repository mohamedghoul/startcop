"""
Corporate Structure Extractor
Extracts company structure, governance, and key personnel
"""

import re
import logging
from typing import List, Optional, Dict, Any

from .base import BaseExtractor
from .models import CorporateStructure, FinancialMetric, ExtractionResult
from .patterns import CORPORATE_PATTERNS

logger = logging.getLogger(__name__)

class CorporateExtractor(BaseExtractor):
    """
    Extracts corporate structure information:
    1. Entity type and registration
    2. Board members and key personnel
    3. Compliance officer
    4. Share capital
    5. Governance policies
    """
    
    def __init__(self):
        super().__init__("CorporateExtractor")
        
        # Initialize patterns
        self.entity_patterns = CORPORATE_PATTERNS['entity_types']
        self.role_patterns = CORPORATE_PATTERNS['roles']
    
    def extract(self, text: str) -> ExtractionResult:
        """
        Extract corporate structure information
        """
        structure = CorporateStructure()
        methods_used = []
        
        # 1. Extract entity type
        entity_type = self._extract_entity_type(text)
        if entity_type:
            structure.entity_type = entity_type
            methods_used.append("entity_type")
        
        # 2. Extract key personnel
        personnel = self._extract_key_personnel(text)
        if personnel:
            structure.board_members = personnel
            methods_used.append("personnel")
        
        # 3. Extract compliance officer
        compliance_officer = self._extract_compliance_officer(text)
        if compliance_officer:
            structure.compliance_officer = compliance_officer
            methods_used.append("compliance")
        
        # 4. Extract share capital
        share_capital = self._extract_share_capital(text)
        if share_capital:
            structure.share_capital = share_capital
            methods_used.append("capital")
        
        # 5. Extract governance policies
        policies = self._extract_governance_policies(text)
        if policies:
            structure.governance_policies = policies
            methods_used.append("policies")
        
        # Calculate confidence based on what was found
        confidence_factors = []
        if structure.entity_type != "Unknown":
            confidence_factors.append(0.9)
        if structure.compliance_officer:
            confidence_factors.append(0.8)
        if structure.board_members:
            confidence_factors.append(0.7)
        if structure.share_capital:
            confidence_factors.append(0.8)
        
        avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
        
        return ExtractionResult(
            entities=[structure],  # Return as single entity
            confidence=avg_confidence,
            method_used="+".join(methods_used),
            processing_time=self.processing_time,
            errors=self.errors
        )
    
    def _extract_entity_type(self, text: str) -> str:
        """Extract company entity type"""
        # Try direct pattern matching first
        for entity_type, pattern in self.entity_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return entity_type
        
        return "Unknown"
    
    def _extract_key_personnel(self, text: str) -> List[str]:
        """Extract board members and key personnel"""
        personnel = []
        
        # Look for management/leadership sections
        management_section = self._find_management_section(text)
        if not management_section:
            management_section = text
        
        # Extract roles and names
        for role, pattern in self.role_patterns.items():
            matches = re.finditer(pattern, management_section, re.IGNORECASE)
            
            for match in matches:
                # Look for name after role
                after_role = management_section[match.end():match.end() + 100]
                name_match = re.search(r':?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', after_role)
                
                if name_match:
                    personnel.append(f"{match.group().strip()}: {name_match.group(1)}")
        
        # Remove duplicates and limit
        seen = set()
        unique_personnel = []
        for person in personnel:
            if person not in seen:
                seen.add(person)
                unique_personnel.append(person)
        
        return unique_personnel[:10]  # Limit to first 10
    
    def _extract_compliance_officer(self, text: str) -> Optional[str]:
        """Extract compliance officer specifically"""
        patterns = [
            r'compliance officer[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'chief compliance officer[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'CCO[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_share_capital(self, text: str) -> Optional[FinancialMetric]:
        """Extract share capital information"""
        capital_patterns = [
            r'(?:authorized|share)\s+capital\s+(?:of\s+)?(?:QAR|\$)?\s*([\d,]+(?:\.\d{2})?)',
            r'paid.up\s+capital\s+(?:of\s+)?(?:QAR|\$)?\s*([\d,]+(?:\.\d{2})?)'
        ]
        
        for pattern in capital_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1).replace(',', ''))
                    return FinancialMetric(
                        metric_type='share_capital',
                        value=value,
                        currency='QAR',
                        description=match.group(0),
                        confidence=0.8
                    )
                except ValueError:
                    continue
        
        return None
    
    def _extract_governance_policies(self, text: str) -> List[str]:
        """Extract governance and compliance policies"""
        policies = []
        
        policy_patterns = {
            'board_charter': r'board charter|governance charter',
            'audit_committee': r'audit committee|audit charter',
            'risk_committee': r'risk committee|risk management committee',
            'compensation_committee': r'compensation committee|remuneration committee',
            'nomination_committee': r'nomination committee|governance committee'
        }
        
        for policy_type, pattern in policy_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                policies.append(policy_type)
        
        return policies
    
    def _find_management_section(self, text: str) -> Optional[str]:
        """Find management/leadership section in text"""
        patterns = [
            r'(?:management|leadership|board|directors?)[\s\w]*:?\s*\n(.*?)(?:\n\n|\n\s*\n)',
            r'(?:key personnel|our team|executives)[\s:]*\n(.*?)(?:\n\n|\n\s*\n)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None