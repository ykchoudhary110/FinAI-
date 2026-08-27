import re
from typing import Dict, List, Optional
from finai.application.orchestration.intent_detector import UserIntent


class ExecutionPlan:
    def __init__(
        self,
        intent: UserIntent,
        rule_function_name: str,
        extracted_slots: Dict[str, float],
        missing_slots: List[str],
        clarifying_question: Optional[str] = None,
    ):
        self.intent = intent
        self.rule_function_name = rule_function_name
        self.extracted_slots = extracted_slots
        self.missing_slots = missing_slots
        self.clarifying_question = clarifying_question
        self.is_ready = len(missing_slots) == 0


def plan_execution(intent: UserIntent, user_text: str) -> ExecutionPlan:
    """
    Planner stage per Section 4:
    Extracts slots from text. If required slots are missing, generates a clear, complete question.
    """
    extracted_slots: Dict[str, float] = {}

    # Extract all numbers from text
    numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", user_text)]

    if intent == UserIntent.CALCULATE_GST:
        missing = []
        if len(numbers) >= 2:
            extracted_slots["amount"] = numbers[0]
            extracted_slots["rate_percent"] = numbers[1]
        elif len(numbers) == 1:
            extracted_slots["amount"] = numbers[0]
            for rate in [5.0, 12.0, 18.0, 28.0]:
                if f"{int(rate)}%" in user_text or f"{int(rate)} percent" in user_text.lower():
                    extracted_slots["rate_percent"] = rate
                    break
            if "rate_percent" not in extracted_slots:
                missing.append("rate_percent")
        else:
            missing.extend(["amount", "rate_percent"])

        if "rate_percent" in missing and "amount" in extracted_slots:
            amt = extracted_slots["amount"]
            question = f"To calculate GST for ₹{amt:,.2f}, please specify the GST rate percentage (e.g. 5%, 12%, 18%, or 28%)."
        elif missing:
            question = "To calculate GST, please specify your base amount in Rupees and the GST rate (e.g. 'GST for ₹10,000 at 18%')."
        else:
            question = None

        return ExecutionPlan(intent, "calculate_gst_forward", extracted_slots, missing, question)

    elif intent == UserIntent.CALCULATE_EMI:
        missing = []
        if len(numbers) >= 3:
            extracted_slots["principal"] = numbers[0]
            extracted_slots["annual_rate"] = numbers[1]
            extracted_slots["tenure_months"] = int(numbers[2])
        else:
            if len(numbers) >= 1:
                extracted_slots["principal"] = numbers[0]
            else:
                missing.append("principal")
            if len(numbers) >= 2:
                extracted_slots["annual_rate"] = numbers[1]
            else:
                missing.append("annual_rate")
            missing.append("tenure_months")

        question = (
            "To compute loan EMIs, please specify the principal loan amount (₹), annual interest rate (%), and tenure in months."
            if missing
            else None
        )
        return ExecutionPlan(intent, "calculate_emi", extracted_slots, missing, question)

    elif intent == UserIntent.CALCULATE_TAX:
        missing = []
        if len(numbers) >= 1:
            extracted_slots["gross_income"] = numbers[0]
        else:
            missing.append("gross_income")

        question = (
            "To estimate your income tax under FY 2025-26 slabs, please enter your total annual gross income in Rupees."
            if missing
            else None
        )
        return ExecutionPlan(intent, "calculate_income_tax", extracted_slots, missing, question)

    else:
        return ExecutionPlan(intent, "general_chat", extracted_slots, [], None)
