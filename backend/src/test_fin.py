# test_fin.py
from document_processor.financial_extractor import FinancialExtractor

txt = """
Al-Ameen Digital LLC – paid-up capital QAR 5,000,000.
Maximum individual loan QAR 200k.
Revenue projection QAR 1.2 billion.
"""

fe = FinancialExtractor()
result = fe.extract(txt)

print("---- RAW ENTITIES ----")
for m in result.entities:
    print(m.dict())

print("---- GAPS (manual) ----")
for m in result.entities:
    if m.metric_type == "share_capital" and m.value < 7_500_000:
        print("CAPITAL_SHORTFALL – found QAR", m.value)