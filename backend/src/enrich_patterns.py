"""
Auto-populate patterns.py with real literals scraped from QFC PDFs
Run once after re-scraping.
"""
import json
import re
from pathlib import Path

# load the big JSON you just generated
kb = json.loads(Path("real_qcb_regulations.json").read_text(encoding="utf-8"))

capital_nums   = set()
officer_titles = set()
locations      = set()
tx_limits      = set()

for cat, rules in kb["regulations"].items():
    if not cat.startswith("qfc_"):
        continue
    for rule in rules:
        txt = rule.get("content", "")
        print("DEBUG:", txt[:200]) 
        # 1. capital amounts (regex on raw text)
        m = re.search(r'(?:paid-up|share|authorized)\s+capital\s+(?:of\s+)?(?:QAR)?\s*([\d,]+)', txt, re.I)
        if m:
            capital_nums.add(m.group(1).replace(",", ""))
        # 2. officer titles (regex on raw text)
        m = re.search(r'compliance officer[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', txt, re.I)
        if m:
            officer_titles.add(m.group(1).strip())
        # 3. locations (simple word search)
        if "ireland" in txt.lower():
            locations.add("ireland")
        if "singapore" in txt.lower():
            locations.add("singapore")
        # 4. transaction limits (regex on raw text)
        m = re.search(r'(?:maximum|up to|limit of)\s+(?:QAR)?\s*([\d,]+)', txt, re.I)
        if m:
            tx_limits.add(m.group(1).replace(",", ""))

# ------------------------------------------------------------------
# inject into patterns.py (append-only so we don't break existing)
patterns_file = Path("document_processor/patterns.py")
patterns_file = Path(__file__).parent / "document_processor" / "patterns.py"
lines = patterns_file.read_text(encoding="utf-8").splitlines()

# find the last line (EOF or MOCK_LITERALS)
insert_at = len(lines)  # append at end
new_blocks = [
    "",
    "# ------------------------------------------------------------------",
    "# 5. REAL REGULATION LITERALS (auto-generated from scrape)",
    "# ------------------------------------------------------------------",
    f"REAL_CAPITAL_AMOUNTS = {list(capital_nums)}",
    f"REAL_OFFICER_TITLES  = {list(officer_titles)}",
    f"REAL_LOCATIONS       = {list(locations)}",
    f"REAL_TX_LIMITS       = {list(tx_limits)}",
]

lines[insert_at:insert_at] = new_blocks
patterns_file.write_text("\n".join(lines), encoding="utf-8")
print("patterns.py enriched with real literals")
print(f"   capital amounts: {len(capital_nums)}")
print(f"   officer titles : {len(officer_titles)}")
print(f"   locations      : {len(locations)}")
print(f"   tx limits      : {len(tx_limits)}")