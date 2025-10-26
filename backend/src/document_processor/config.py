# src/document_processor/config.py
"""
Configuration for Document Processor
"""

# This needs to be MODEL_SETTINGS to match the import
MODEL_SETTINGS = {
    'activity_classifier': {
        'model': 'facebook/bart-large-mnli',        # keep
        'confidence_threshold': 0.10
    },
    'financial_ner': {
        'model': 'dslim/bert-large-NER',            # upgrade: large
        'confidence_threshold': 0.10
    },
    'amount_extractor': {
        'model': 'deepset/roberta-large-squad2',    # upgrade: large
        'confidence_threshold': 0.05
    }
}

# Business Activity Keywords
BUSINESS_ACTIVITIES = {
    'p2p_lending': {
        'keywords': [
            'peer to peer', 'p2p', 'crowdfunding', 'marketplace lending',
            'loan origination', 'direct lending', 'alternative lending',
            'investor borrower', 'lending platform'
        ],
        'weight': 1.0
    },
    
    'payment_processing': {
        'keywords': [
            'payment gateway', 'payment processor', 'digital payments',
            'mobile payments', 'cross border payments', 'remittance',
            'wire transfer', 'swift', 'payment infrastructure'
        ],
        'weight': 1.0
    },
    
    'digital_wallet': {
        'keywords': [
            'digital wallet', 'e wallet', 'mobile wallet', 'virtual wallet',
            'stored value', 'prepaid', 'electronic money'
        ],
        'weight': 0.9
    },
    
    'investment_platform': {
        'keywords': [
            'investment platform', 'robo advisor', 'wealth management',
            'portfolio management', 'asset management', 'digital wealth'
        ],
        'weight': 0.9
    }
}

# Financial Patterns
FINANCIAL_PATTERNS = {
    'capital_requirement': r'(?:paid-up|share|authorized)\s+capital.*?QAR\s*([\d,]*\d[\d,]*)(?:\s*([mkb]|million|billion|thousand))?',
    'transaction_limit': r'(?:maximum|up to|limit of|capped at).*?QAR\s*([\d,]*\d[\d,]*)(?:\s*([mkb]|million|billion|thousand))?',
    'revenue_projection': r'(?:revenue|turnover|income).*?QAR\s*([\d,]*\d[\d,]*)(?:\s*([mkb]|million|billion|thousand))?',
    'fee_structure': r'(?:fee|commission|charge).*?QAR\s*([\d,]*\d[\d,]*)(?:\s*([mkb]|million|billion|thousand))?%?'
}

# Corporate Structure Patterns
CORPORATE_PATTERNS = {
    'entity_types': {
        'LLC': r'(?:limited liability company|llc|wll)',
        'JSC': r'(?:joint stock company|jsc)',
        'PARTNERSHIP': r'(?:general|limited) partnership',
        'SOLE': r'sole proprietorship'
    },
    
    'roles': {
        'CEO': r'(?:chief executive|ceo|managing director)',
        'CFO': r'(?:chief financial|cfo|finance director)',
        'CTO': r'(?:chief technology|cto)',
        'COMPLIANCE_OFFICER': r'(?:compliance officer|cco)'
    }
}

# Confidence Thresholds
CONFIDENCE_THRESHOLDS = {
    'high': 0.5,
    'medium': 0.3,
    'low': 0.2,
    'minimum': 0.1
}

# Processing Settings
PROCESSING_CONFIG = {
    'max_text_chunk_size': 512,
    'overlap_size': 50,
    'max_entities_per_type': 50,
    'min_sentence_length': 20
}