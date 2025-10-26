"""
All regex patterns and keywords used for entity extraction
Organized by category for easy maintenance
"""

# Business Activity Keywords
BUSINESS_ACTIVITIES = {
    'p2p_lending': {
        'keywords': [
            'peer to peer', 'p2p', 'crowdfunding', 'marketplace lending',
            'loan origination', 'direct lending', 'alternative lending'
        ],
        'weight': 1.0,
        'description': 'Direct lending between parties'
    },
    
    'payment_processing': {
        'keywords': [
            'payment gateway', 'payment processor', 'digital payments',
            'mobile payments', 'cross border payments', 'remittance'
        ],
        'weight': 1.0,
        'description': 'Payment infrastructure and processing'
    },
    
    'digital_wallet': {
        'keywords': [
            'digital wallet', 'e wallet', 'mobile wallet', 'stored value'
        ],
        'weight': 0.9,
        'description': 'Electronic wallet services'
    }
}

# Financial Patterns
FINANCIAL_PATTERNS = {
    'capital_requirement': {
        'pattern': r'(?:minimum\s+)?(?:paid.up|share|authorized)\s+capital\s+(?:of\s+)?(?:QAR|[\d,]+)',
        'context_keywords': ['capital', 'equity', 'share']
    },
    
    'transaction_limit': {
        'pattern': r'(?:maximum|up to|limit of)\s+(?:QAR|\$)?\s*[\d,]+',
        'context_keywords': ['limit', 'maximum', 'up to']
    },
    
    'revenue_projection': {
        'pattern': r'(?:revenue|turnover|income)\s+(?:of\s+)?(?:QAR|\$)?\s*[\d,]+',
        'context_keywords': ['revenue', 'income', 'turnover']
    }
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

# ------------------------------------------------------------------
# 5. REAL REGULATION LITERALS (auto-generated from scrape)
# ------------------------------------------------------------------
REAL_CAPITAL_AMOUNTS = []
REAL_OFFICER_TITLES  = []
REAL_LOCATIONS       = []
REAL_TX_LIMITS       = []

# ------------------------------------------------------------------
# 5. REAL REGULATION LITERALS (auto-generated from scrape)
# ------------------------------------------------------------------
REAL_CAPITAL_AMOUNTS = []
REAL_OFFICER_TITLES  = ['to confirm that the insurer is authorised to provide or sell the product']
REAL_LOCATIONS       = []
REAL_TX_LIMITS       = []

# ------------------------------------------------------------------
# 5. REAL REGULATION LITERALS (auto-generated from scrape)
# ------------------------------------------------------------------
REAL_CAPITAL_AMOUNTS = []
REAL_OFFICER_TITLES  = ['to confirm that the insurer is authorised to provide or sell the product']
REAL_LOCATIONS       = []
REAL_TX_LIMITS       = []