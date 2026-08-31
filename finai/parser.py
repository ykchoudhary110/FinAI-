from __future__ import annotations
import re
from finai.catalog import find_candidates

QUICK_PICKS = [
    {"label": "💻 IT / Software Services (18%)", "code": "998313"},
    {"label": "🪑 Office Furniture (18%)", "code": "9403"},
    {"label": "🖥️ Computers & Laptops (18%)", "code": "8471"},
    {"label": "🚚 Goods Transport / GTA (5%)", "code": "996511"},
    {"label": "💊 Medicines & Pharma (12%)", "code": "3004"},
    {"label": "🚗 Motor Vehicle (28%)", "code": "8703"},
    {"label": "🏗️ Cement (28%)", "code": "2501"},
    {"label": "📖 Books (Exempt)", "code": "4901"},
]


def parse_transaction(text: str) -> dict:
    normalized = text.lower().replace("₹", " ")
    normalized = re.sub(r"\brs\.?\s*", " ", normalized)
    amounts = re.findall(r"(?<!\w)(\d[\d,]*(?:\.\d+)?)", normalized)
    amount = float(amounts[-1].replace(",", "")) if amounts else None
    purchase = any(word in normalized for word in ("bought", "purchased", "purchase", "paid for", "expense", "inward"))
    interstate = any(word in normalized for word in ("interstate", "igst", "outside state", "to mumbai", "to delhi", "to bangalore", "to chennai", "to kolkata", "other state", "mumbai to", "delhi to"))
    candidates = find_candidates(normalized)
    
    needs_classification = (amount is not None and len(candidates) == 0)
    
    return {
        "raw": text,
        "amount": amount,
        "transaction_type": "purchase" if purchase else "sale",
        "interstate": interstate,
        "candidates": candidates,
        "needs_classification": needs_classification,
        "quick_picks": QUICK_PICKS if needs_classification else [],
    }
