"""
Real QCB Regulatory Knowledge Base Scraper
Fetches actual regulations from official QCB, QFC & FATF sources
"""
import os
import tempfile
import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class QCBKnowledgeBaseScraper:
    def __init__(self):
        self.base_url = "https://www.qcb.gov.qa"
        self.regulatory_urls = {
            # ----- QCB (HTML) -----
            'fintech': "https://www.qcb.gov.qa/en/Pages/FinancialTechnology.aspx",
            'legislation': "https://www.qcb.gov.qa/en/legislation/Pages/LegislationNew.aspx",
            'security': "https://www.qcb.gov.qa/en/Pages/Information-Security.aspx",
            'aml': "https://www.qcb.gov.qa/en/Pages/AML-CFT.aspx",
            'licensing': "https://www.qcb.gov.qa/en/Pages/Licensing.aspx",
            'consumer_protection': "https://www.qcb.gov.qa/en/Pages/ConsumerProtection.aspx",

            # ----- QFC (PDF) -----
            'qfc_aml': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_12506_VER5.pdf",
            'qfc_insurance_aml': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/AMLG-VER4-January20_closed.pdf",
            'qfc_banking': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_9582_VER94.pdf",
            'qfc_captive_insurance': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_8125_VER9.pdf",
            'qfc_customer_protection': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_12179_VER5.pdf",
            'qfc_derivatives': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_13578_VER03.pdf",
            'qfc_general_rules': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_3828_VER29.pdf",
            'qfc_governance': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_9107_VER7.pdf",
            'qfc_islamic_banking': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_10464_VER11.pdf",
            'qfc_investment_management': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_9583_VER9.pdf",
            'qfc_investment_token': "https://qfcra-en.thomsonreuters.com/sites/default/files/net_file_store/QFCRA_15114_VER1.pdf",

            # ----- FATF -----
            'fatf_recommendations': "https://www.fatf-gafi.org/content/dam/fatf-gafi/recommendations/FATF%20Recommendations%202012.pdf.coredownload.inline.pdf"
        }

    # -------------------- public API --------------------
    def scrape_all_regulations(self) -> Dict[str, List[Dict[str, Any]]]:
        all_regulations = {}
        for category, url in self.regulatory_urls.items():
            print(f"Scraping {category} from {url}")
            try:
                regulations = self._scrape_category(url, category)
                all_regulations[category] = regulations
                print(f"{category}: {len(regulations)} items")
            except Exception as e:
                print(f"{category} failed: {e}")
                all_regulations[category] = []
        return all_regulations

    # -------------------- internal scrapers --------------------
    def _scrape_category(self, url: str, category: str) -> List[Dict[str, Any]]:
        if category.startswith(('qfc_', 'fatf_')):   # PDF branch
            return self._parse_pdf_regulation(url, category)

        # HTML branch (legacy)
        try:
            resp = requests.get(url, timeout=30, headers={'User-Agent': 'RegulatoryNavigator/1.0'})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
        except Exception as e:
            logger.error(f"HTTP error on {url}: {e}")
            return []

        parsers = {
            'fintech': self._parse_fintech_regulations,
            'legislation': self._parse_legislation,
            'security': self._parse_security_requirements,
            'aml': self._parse_aml_requirements,
            'licensing': self._parse_licensing_requirements,
            'consumer_protection': self._parse_consumer_protection,
        }
        return parsers.get(category, lambda _: [])(soup)

    # -------------------- HTML parsers --------------------
    def _parse_fintech_regulations(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        regulations = []
        containers = soup.find_all('div', class_=lambda x: x and 'content' in x) or [soup]
        for box in containers:
            for h in box.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                reg = self._extract_regulation_from_heading(h)
                if reg:
                    regulations.append(reg)
            for a in box.find_all('a', href=lambda h: h and '.pdf' in h.lower()):
                regulations.append({
                    'title': a.get_text(strip=True),
                    'url': self._resolve_url(a['href']),
                    'type': 'pdf_document',
                    'category': 'fintech',
                    'summary': f"QCB Fintech PDF: {a.get_text(strip=True)}",
                    'extracted_requirements': {}
                })
        return regulations

    def _parse_legislation(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        regulations = []
        for section in soup.find_all(lambda t: t.name == 'div' and 'legislation' in (t.get('class', []) or [])):
            for item in section.find_all(['div', 'li', 'p'], class_=lambda x: x and 'item' in x):
                title_elem = item.find(['h3', 'h4', 'strong'])
                if title_elem:
                    content = item.get_text(strip=True)
                    regulations.append({
                        'title': title_elem.get_text(strip=True),
                        'content': content,
                        'type': 'legislation',
                        'category': 'general',
                        'summary': self._generate_summary(content),
                        'extracted_requirements': self._extract_structured_requirements(content)
                    })
        return regulations

    def _parse_security_requirements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        regulations = []
        for section in soup.find_all(['div', 'section']):
            if not any(term in section.get_text('', '').lower() for term in
                       ['security', 'cyber', 'information', 'data protection']):
                continue
            for p in section.find_all(['p', 'li', 'div']):
                txt = p.get_text(strip=True)
                if len(txt) > 20:
                    regulations.append({
                        'title': self._extract_security_title(txt),
                        'content': txt,
                        'type': 'security_requirement',
                        'category': 'information_security',
                        'summary': self._generate_summary(txt),
                        'extracted_requirements': self._extract_structured_requirements(txt)
                    })
        return regulations

    def _parse_aml_requirements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        regulations = []
        for section in soup.find_all(['div', 'section']):
            if not any(term in section.get_text('', '').lower() for term in
                       ['aml', 'cft', 'anti-money', 'laundering']):
                continue
            for p in section.find_all(['p', 'li']):
                txt = p.get_text(strip=True)
                if 'AML' in txt or 'CFT' in txt or len(txt) > 30:
                    regulations.append({
                        'title': self._extract_aml_title(txt),
                        'content': txt,
                        'type': 'aml_requirement',
                        'category': 'aml_cft',
                        'summary': self._generate_summary(txt),
                        'extracted_requirements': self._extract_structured_requirements(txt)
                    })
        return regulations

    def _parse_licensing_requirements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        regulations = []
        for section in soup.find_all(['div', 'section']):
            if 'licens' not in section.get_text('', '').lower():
                continue
            for p in section.find_all(['p', 'li', 'div']):
                txt = p.get_text(strip=True)
                if 'license' in txt.lower() and len(txt) > 20:
                    regulations.append({
                        'title': self._extract_licensing_title(txt),
                        'content': txt,
                        'type': 'licensing_requirement',
                        'category': 'licensing',
                        'summary': self._generate_summary(txt),
                        'extracted_requirements': {
                            'capital_requirement': self._extract_capital_requirement(txt),
                            'license_fees': self._extract_license_fees(txt),
                            'compliance_requirements': self._extract_structured_requirements(txt).get('compliance_requirements', [])
                        }
                    })
        return regulations

    def _parse_consumer_protection(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        regulations = []
        for section in soup.find_all(['div', 'section']):
            if 'consumer protection' not in section.get_text('', '').lower():
                continue
            txt = section.get_text(strip=True)
            regulations.append({
                'title': self._extract_consumer_protection_title(txt),
                'content': txt,
                'type': 'consumer_protection',
                'category': 'consumer_protection',
                'summary': self._generate_summary(txt),
                'extracted_requirements': self._extract_structured_requirements(txt)
            })
        return regulations

    # -------------------- PDF parser --------------------
    def _parse_pdf_regulation(self, url: str, category: str) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(url, timeout=60, headers={'User-Agent': 'RegulatoryNavigator/1.0'})
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"PDF download failed {url}: {e}")
            return []

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name

        try:
            from document_processor.parser import DocumentParser
            text = DocumentParser().parse_document(tmp_path)
        except Exception as e:
            logger.error(f"PDF parse failed {url}: {e}")
            text = ""
        finally:
            os.unlink(tmp_path)

        return [{
            'title': category.replace('_', ' ').title(),
            'content': text,
            'type': 'pdf_regulation',
            'category': category,
            'summary': self._generate_summary(text),
            'extracted_requirements': self._extract_structured_requirements(text)
        }]

    # -------------------- helpers --------------------
    def _extract_regulation_from_heading(self, heading):
        title = heading.get_text(strip=True)
        if not title:
            return None
        content_node = heading.find_next_sibling(['p', 'div'])
        content = content_node.get_text(strip=True) if content_node else ""
        return {
            'title': title,
            'content': content,
            'type': 'heading_section',
            'category': 'fintech',
            'summary': self._generate_summary(content),
            'extracted_requirements': self._extract_structured_requirements(content)
        }

    def _extract_consumer_protection_title(self, text: str) -> str:
        match = re.search(r'consumer protection[\s:–-]*([A-Z].{0,80})', text, re.I)
        return match.group(1).strip() if match else "Consumer Protection Regulation"

    def _extract_security_title(self, text: str) -> str:
        match = re.search(r'(information security|cyber security|data protection)[\s:–-]*([A-Z].{0,80})', text, re.I)
        return match.group(0).strip() if match else "Information Security Requirement"

    def _extract_aml_title(self, text: str) -> str:
        match = re.search(r'(AML|anti-money laundering|CFT)[\s:–-]*([A-Z].{0,80})', text, re.I)
        return match.group(0).strip() if match else "AML/CFT Requirement"

    def _extract_licensing_title(self, text: str) -> str:
        match = re.search(r'(licensing|licence)[\s:–-]*([A-Z].{0,80})', text, re.I)
        return match.group(0).strip() if match else "Licensing Requirement"

    def _extract_structured_requirements(self, text: str) -> Dict[str, Any]:
        requirements = {}
        capital_match = re.search(r'(?:minimum\s+)?(?:paid-up|share|authorized)\s+capital\s+(?:of\s+)?(?:QAR|\$)?\s*([\d,]+(?:\.\d{2})?)', text, re.I)
        if capital_match:
            requirements['capital_requirement'] = {
                'amount': float(capital_match.group(1).replace(',', '')),
                'currency': 'QAR' if 'QAR' in capital_match.group(0) else 'USD'
            }
        limit_match = re.search(r'(?:maximum|up to|limit of)\s+(?:QAR|\$)?\s*([\d,]+(?:\.\d{2})?)', text, re.I)
        if limit_match:
            requirements['transaction_limit'] = {
                'amount': float(limit_match.group(1).replace(',', '')),
                'currency': 'QAR' if 'QAR' in limit_match.group(0) else 'USD'
            }
        fee_matches = re.finditer(r'([\d.]+%?)\s*(?:fee|commission|charge)', text, re.I)
        fees = [m.group(1) for m in fee_matches]
        if fees:
            requirements['fees'] = fees
        compliance_reqs = []
        for kw in ['AML|anti-money laundering', 'KYC|know your customer', 'data protection|privacy',
                   'compliance officer|chief compliance', 'data residency|local storage']:
            if re.search(kw, text, re.I):
                compliance_reqs.append(kw.split('|')[0].upper())
        if compliance_reqs:
            requirements['compliance_requirements'] = compliance_reqs
        return requirements

    def _extract_capital_requirement(self, text: str) -> Optional[Dict[str, Any]]:
        match = re.search(r'(?:minimum\s+)?(?:paid-up|share|authorized)\s+capital\s+(?:of\s+)?(?:QAR|\$)?\s*([\d,]+(?:\.\d{2})?)', text, re.I)
        if match:
            return {
                'amount': float(match.group(1).replace(',', '')),
                'currency': 'QAR' if 'QAR' in match.group(0) else 'USD'
            }
        return None

    def _extract_license_fees(self, text: str) -> List[str]:
        fee_matches = re.finditer(r'([\d.]+%?)\s*(?:fee|charge|cost)', text, re.I)
        return [match.group(1) for match in fee_matches]

    def _generate_summary(self, text: str) -> str:
        return (text[:200] + '...') if len(text) > 200 else text

    def _resolve_url(self, url: str) -> str:
        return url if url.startswith('http') else self.base_url + url

    # ------------------------------------------------------------------
    def save_knowledge_base(self, regulations: Dict[str, List[Dict[str, Any]]],
                          filename: str = 'src/real_qcb_regulations.json'):
        knowledge_base = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'total_regulations': sum(len(regs) for regs in regulations.values()),
                'categories': list(regulations.keys()),
                'source': 'QCB_QFC_FATF'
            },
            'regulations': regulations
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        print(f"Knowledge base saved to {filename}")
        return knowledge_base


if __name__ == "__main__":
    scraper = QCBKnowledgeBaseScraper()
    regulations = scraper.scrape_all_regulations()
    knowledge_base = scraper.save_knowledge_base(regulations)
    print(f"Total regulations scraped: {knowledge_base['metadata']['total_regulations']}")
    for category, regs in regulations.items():
        print(f"{category}: {len(regs)} regulations")