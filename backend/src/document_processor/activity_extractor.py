"""
Business Activity Extractor
Uses transformer models for high-accuracy classification
"""
import re
import logging
from typing import List
import torch
from transformers import pipeline

from .base import BaseExtractor
from .models import BusinessActivity, ExtractionResult
from .config import BUSINESS_ACTIVITIES, MODEL_SETTINGS

logger = logging.getLogger(__name__)

class BusinessActivityExtractor(BaseExtractor):
    """Extract business activities using transformer models"""
    
    def __init__(self):
        super().__init__("BusinessActivityExtractor")
        
        # Load transformer model
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model=MODEL_SETTINGS['activity_classifier']['model'],
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ Activity classifier loaded")
        except Exception as e:
            logger.error(f"Failed to load activity classifier: {e}")
            self.classifier = None
    
    def extract(self, text: str) -> ExtractionResult:
        """Extract business activities"""
        activities = []
        
        # 1. Transformer classification (primary method)
        if self.classifier:
            transformer_activities = self._classify_with_transformer(text)
            activities.extend(transformer_activities)
        
        # 2. Keyword fallback
        keyword_activities = self._extract_keywords(text)
        activities.extend(keyword_activities)
        
        # Remove duplicates
        unique_activities = self._deduplicate_activities(activities)
        
        # Calculate confidence
        avg_confidence = sum(a.confidence for a in unique_activities) / len(unique_activities) if unique_activities else 0.0
        
        return ExtractionResult(
            entities=unique_activities,
            confidence=avg_confidence,
            method_used="transformer+keywords",
            processing_time=self.processing_time,
            errors=self.errors
        )
    
    def _classify_with_transformer(self, text: str) -> List[BusinessActivity]:
        """Use transformer for classification"""
        activities = []
        
        # Split into chunks
        chunks = self._split_text(text, max_length=400)
        candidate_labels = list(BUSINESS_ACTIVITIES.keys())
        
        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue
            
            try:
                result = self.classifier(chunk, candidate_labels, multi_label=True)
                
                for label, score in zip(result['labels'], result['scores']):
                    if score >= MODEL_SETTINGS['activity_classifier']['confidence_threshold']:
                        activity = BusinessActivity(
                            activity_type=label,
                            description=chunk[:200],
                            confidence=score,
                            source_method="transformer"
                        )
                        activities.append(activity)
                        
            except Exception as e:
                logger.warning(f"Classification failed: {e}")
                self.errors.append(str(e))
        
        return activities
    
    def _extract_keywords(self, text: str) -> List[BusinessActivity]:
        """Extract using keyword matching"""
        activities = []
        
        for activity_type, config in BUSINESS_ACTIVITIES.items():
            matches = 0
            
            for keyword in config['keywords']:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches += len(re.findall(pattern, text, re.IGNORECASE))
            
            if matches > 0:
                confidence = min(0.7, matches * config['weight'] * 0.2)
                
                activity = BusinessActivity(
                    activity_type=activity_type,
                    description=f"Found {matches} mentions of {activity_type}",
                    confidence=confidence,
                    source_method="keywords"
                )
                activities.append(activity)
        
        return activities
    
    def _split_text(self, text: str, max_length: int = 400) -> List[str]:
        """Split text into chunks"""
        sentences = text.replace('\n', ' ').split('.')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            words = sentence.split()
            if current_length + len(words) > max_length and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = []
                current_length = 0
            
            current_chunk.append(sentence)
            current_length += len(words)
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def _deduplicate_activities(self, activities: List[BusinessActivity]) -> List[BusinessActivity]:
        """Remove duplicate activities"""
        seen = {}
        
        for activity in activities:
            key = activity.activity_type
            if key not in seen or activity.confidence > seen[key].confidence:
                seen[key] = activity
        
        return list(seen.values())