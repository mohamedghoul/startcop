"""
Base Extractor - All extractors inherit from this
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Any

from .models import ExtractionResult

logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """Base class for all entity extractors"""
    
    def __init__(self, name: str):
        self.name = name
        self.processing_time = 0.0
        self.errors = []
    
    def process_with_error_handling(self, text: str) -> ExtractionResult:
        """Process with error handling and timing"""
        start_time = time.time()
        self.errors = []
        
        try:
            if not text or not text.strip():
                raise ValueError("Empty text provided")
            
            result = self.extract(text)
            result.processing_time = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Extraction failed in {self.name}: {e}")
            self.errors.append(str(e))
            
            return ExtractionResult(
                entities=[],
                confidence=0.0,
                method_used=self.name,
                processing_time=time.time() - start_time,
                errors=self.errors
            )
    
    @abstractmethod
    def extract(self, text: str) -> ExtractionResult:
        """Main extraction method - implement in subclasses"""
        pass