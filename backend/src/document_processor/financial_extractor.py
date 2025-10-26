# src/document_processor/financial_extractor.py
"""
Financial Metrics Extractor
Specialised in extracting financial amounts, currencies, and metrics
"""
import re
import logging
from typing import List, Dict, Any, Optional
import torch
from transformers import pipeline

from .base import BaseExtractor
from .models import FinancialMetric, ExtractionResult
from .config import FINANCIAL_PATTERNS, MODEL_SETTINGS

logger = logging.getLogger(__name__)

class FinancialExtractor(BaseExtractor):
    """Extracts financial metrics using transformer models + rule-based fallback"""

    def __init__(self):
        super().__init__("FinancialExtractor")
        self._load_models()
        self.currency_symbols = {
            'QAR': ['QAR', 'QR', 'ريال'],
            'USD': ['$', 'USD', 'US$', 'dollar'],
            'EUR': ['€', 'EUR', 'euro'],
            'GBP': ['£', 'GBP', 'pound']
        }

    # ------------------------------------------------------------------
    # Model initialisation
    # ------------------------------------------------------------------
    def _load_models(self):
        try:
            self.financial_ner = pipeline(
                "ner",
                model=MODEL_SETTINGS['financial_ner']['model'],
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Financial NER model loaded")
        except Exception as e:
            logger.warning(f"Financial NER unavailable, fallback: {e}")
            self.financial_ner = None

        try:
            self.qa_model = pipeline(
                "question-answering",
                model=MODEL_SETTINGS['amount_extractor']['model'],
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("QA model loaded")
        except Exception as e:
            logger.warning(f"QA model unavailable: {e}")
            self.qa_model = None

    # ------------------------------------------------------------------
    # Main entry
    # ------------------------------------------------------------------
    def extract(self, text: str) -> ExtractionResult:
        metrics: List[FinancialMetric] = []
        methods_used: List[str] = []

        if self.financial_ner:
            ner_metrics = self._extract_ner(text)
            metrics.extend(ner_metrics)
            if ner_metrics:
                methods_used.append("ner")

        regex_metrics = self._extract_regex(text)
        metrics.extend(regex_metrics)
        if regex_metrics:
            methods_used.append("regex")

        if self.qa_model:
            qa_metrics = self._extract_qa(text)
            metrics.extend(qa_metrics)
            if qa_metrics:
                methods_used.append("qa")

        final_metrics = self._normalize_metrics(metrics)

        avg_confidence = (
            sum(m.confidence for m in final_metrics) / len(final_metrics)
            if final_metrics else 0.0
        )

        return ExtractionResult(
            entities=final_metrics,
            confidence=avg_confidence,
            method_used="+".join(methods_used) if methods_used else "none",
            processing_time=self.processing_time,
            errors=self.errors
        )

    # ------------------------------------------------------------------
    # NER branch
    # ------------------------------------------------------------------
    def _extract_ner(self, text: str) -> List[FinancialMetric]:
        if not self.financial_ner:
            return []

        metrics = []
        try:
            for entity in self.financial_ner(text):
                if entity.get('entity_group') in {'MONEY', 'PERCENT', 'ORG'}:
                    parsed = self._parse_financial_entity(entity['word'], text)
                    if parsed:
                        context = self._get_context(text, entity['start'], entity['end'])
                        metrics.append(
                            FinancialMetric(
                                metric_type=self._classify_financial_type(context),
                                value=parsed['value'],
                                currency=parsed.get('currency', 'QAR'),
                                description=context,
                                confidence=parsed.get('confidence', 0.7)
                            )
                        )
        except Exception as e:
            logger.warning(f"NER extraction failed: {e}")
            self.errors.append(f"NER: {e}")
        return metrics

    # ------------------------------------------------------------------
    # Regex branch
    # ------------------------------------------------------------------
    def _extract_regex(self, text: str) -> List[FinancialMetric]:
        metrics = []
        for metric_type, pattern in FINANCIAL_PATTERNS.items():
            for match in re.finditer(pattern, text, re.I):
                try:
                    parsed = self._parse_amount(match.group())
                    if parsed:
                        context = self._get_context(text, match.start(), match.end())
                        if self._validate_context(context, self._get_context_keywords(metric_type)):
                            metrics.append(
                                FinancialMetric(
                                    metric_type=metric_type,
                                    value=parsed['value'],
                                    currency=parsed.get('currency', 'QAR'),
                                    description=match.group().strip(),
                                    timeframe=self._extract_timeframe(context),
                                    confidence=parsed.get('confidence', 0.6)
                                )
                            )
                except Exception as e:
                    logger.warning(f"Regex parsing failed for {metric_type}: {e}")
        return metrics

    # ------------------------------------------------------------------
    # QA branch
    # ------------------------------------------------------------------
    def _extract_qa(self, text: str) -> List[FinancialMetric]:
        if not self.qa_model:
            return []

        questions = [
            ("What is the minimum capital requirement?", "capital_requirement"),
            ("What is the maximum transaction limit?", "transaction_limit"),
            ("What is the projected revenue?", "revenue_projection"),
            ("What are the fees charged?", "fee_structure")
        ]

        metrics = []
        for question, metric_type in questions:
            try:
                result = self.qa_model(question=question, context=text)
                if result['score'] >= MODEL_SETTINGS['amount_extractor']['confidence_threshold']:
                    parsed = self._parse_amount(result['answer'])
                    if parsed:
                        metrics.append(
                            FinancialMetric(
                                metric_type=metric_type,
                                value=parsed['value'],
                                currency=parsed.get('currency', 'QAR'),
                                description=f"Q: {question} A: {result['answer']}",
                                confidence=result['score']
                            )
                        )
            except Exception as e:
                logger.warning(f"QA extraction failed for {metric_type}: {e}")
        return metrics

    # ------------------------------------------------------------------
    # Amount / currency / multiplier parsing
    # ------------------------------------------------------------------
    def _parse_financial_entity(self, entity_text: str, full_text: str) -> Optional[Dict[str, Any]]:
        entity_text = entity_text.strip()
        amount = self._parse_amount(entity_text)
        if amount:
            return amount

        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', entity_text)
        if percent_match:
            return {'value': float(percent_match.group(1)), 'currency': '%', 'confidence': 0.8}
        return None

    def _parse_amount(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()

        # QAR branch
        qar_match = re.search(
            r'QAR\s*([\d,]*\d[\d,]*)(?:\s*([mkb]|million|billion|thousand))?', text, re.I
        )
        if qar_match:
            digits = qar_match.group(1).replace(',', '')
            if not digits:
                return None
            value = float(digits)
            multiplier = self._get_multiplier((qar_match.group(2) or '') + ' ' + text)
            return {'value': value * multiplier, 'currency': 'QAR', 'confidence': 0.9}

        # USD branch
        usd_match = re.search(
            r'\$?\s*([\d,]*\d[\d,]*)(?:\s*([mkb]|million|billion|thousand))?', text, re.I
        )
        if usd_match:
            digits = usd_match.group(1).replace(',', '')
            if not digits:
                return None
            value = float(digits)
            multiplier = self._get_multiplier((usd_match.group(2) or '') + ' ' + text)
            return {'value': value * multiplier, 'currency': 'USD', 'confidence': 0.8}

        return None

    def _get_multiplier(self, text: str) -> float:
        t = text.lower()
        if any(x in t for x in ('million', 'm')):
            return 1_000_000
        if any(x in t for x in ('billion', 'b')):
            return 1_000_000_000
        if any(x in t for x in ('thousand', 'k')):
            return 1_000
        return 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_context(self, text: str, start: int, end: int, size: int = 100) -> str:
        return text[max(0, start - size):min(len(text), end + size)].strip()

    def _validate_context(self, context: str, keywords: List[str]) -> bool:
        context_lower = context.lower()
        return any(k.lower() in context_lower for k in keywords)

    def _classify_financial_type(self, context: str) -> str:
        context_lower = context.lower()
        if any(w in context_lower for w in ('capital', 'equity', 'share')):
            return 'capital_requirement'
        if any(w in context_lower for w in ('limit', 'maximum', 'up to')):
            return 'transaction_limit'
        if any(w in context_lower for w in ('revenue', 'income', 'turnover')):
            return 'revenue_projection'
        if any(w in context_lower for w in ('fee', 'commission', 'charge')):
            return 'fee_structure'
        return 'general_financial'

    def _extract_timeframe(self, context: str) -> Optional[str]:
        for pattern in [
            r'(?:per|each|every)\s+(?:month|quarter|year|annum)',
            r'(?:monthly|quarterly|annually|yearly)',
            r'(?:first|next)\s+(?:\d+\s+)?(?:month|quarter|year)',
            r'\b\d{4}\b'
        ]:
            match = re.search(pattern, context, re.I)
            if match:
                return match.group(0)
        return None

    def _get_context_keywords(self, metric_type: str) -> List[str]:
        return {
            'capital_requirement': ['capital', 'equity', 'share'],
            'transaction_limit': ['limit', 'maximum', 'up to'],
            'revenue_projection': ['revenue', 'income', 'turnover'],
            'fee_structure': ['fee', 'commission', 'charge']
        }.get(metric_type, [])

    def _normalize_metrics(self, metrics: List[FinancialMetric]) -> List[FinancialMetric]:
        normalized = []
        seen = set()
        for m in metrics:
            if m.value <= 0 or m.value > 1e12:
                continue
            if m.currency not in {'QAR', 'USD', 'EUR', '%'}:
                m.currency = 'QAR'
            key = f"{m.metric_type}_{m.value}_{m.currency}"
            if key not in seen:
                seen.add(key)
                normalized.append(m)
        return normalized