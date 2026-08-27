import re
from enum import Enum
from typing import Optional


class UserIntent(str, Enum):
    CALCULATE_GST = "calculate_gst"
    CALCULATE_TAX = "calculate_tax"
    CALCULATE_EMI = "calculate_emi"
    SCAN_RECEIPT = "scan_receipt"
    BUDGET_ADVICE = "budget_advice"
    INVESTMENT_PLAN = "investment_plan"
    BUSINESS_ADVICE = "business_advice"
    EXPLAIN_NUMBER = "explain_number"
    GENERAL_FINANCE_CHAT = "general_finance_chat"


# Fast keyword-to-intent lookup table for 80% instant resolution
KEYWORD_INTENT_MAP = [
    (r"\b(gst|cgst|sgst|igst|tax invoice)\b", UserIntent.CALCULATE_GST),
    (r"\b(income tax|tax slab|regime|80c|80d|tax payable|tax savings|itr)\b", UserIntent.CALCULATE_TAX),
    (r"\b(emi|loan|amortization|interest rate|tenure|monthly payment)\b", UserIntent.CALCULATE_EMI),
    (r"\b(receipt|scan bill|invoice ocr|ocr|upload receipt)\b", UserIntent.SCAN_RECEIPT),
    (r"\b(budget|savings goal|monthly budget|overspend)\b", UserIntent.BUDGET_ADVICE),
    (r"\b(sip|fd|rd|ppf|nps|mutual fund|investment)\b", UserIntent.INVESTMENT_PLAN),
    (r"\b(working capital|cash flow|inventory turnover|profit margin|business advisor)\b", UserIntent.BUSINESS_ADVICE),
]


def detect_intent_fast(user_text: str) -> Optional[UserIntent]:
    """
    Stage 1: Fast rule-based/keyword classifier using Regex.
    Keeps 80% of interactions instant without LLM latency.
    """
    text_lower = user_text.lower().strip()
    for pattern, intent in KEYWORD_INTENT_MAP:
        if re.search(pattern, text_lower):
            return intent
    return None


def detect_intent(user_text: str, ollama_client=None) -> UserIntent:
    """
    Two-stage Intent Detection per Section 4 of FinAI Specification.
    """
    fast_result = detect_intent_fast(user_text)
    if fast_result:
        return fast_result

    # Stage 2: Fall back to local Ollama if keyword lookup is ambiguous
    if ollama_client:
        try:
            prompt = f"Classify the financial intent of this message: '{user_text}'. Return one of: calculate_gst, calculate_tax, calculate_emi, scan_receipt, budget_advice, investment_plan, business_advice, general_finance_chat. Return ONLY the intent string."
            response = ollama_client.generate(model="qwen2.5:3b", prompt=prompt)
            clean_resp = response.get("response", "").strip().lower()
            for intent in UserIntent:
                if intent.value in clean_resp:
                    return intent
        except Exception:
            pass

    return UserIntent.GENERAL_FINANCE_CHAT
