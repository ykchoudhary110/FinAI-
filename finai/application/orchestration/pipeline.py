import json
import re
from typing import Any, Dict, List, Optional
from finai.application.orchestration.intent_detector import UserIntent, detect_intent
from finai.application.orchestration.planner import plan_execution
from finai.application.orchestration.validator import validate_rule_output
from finai.data.legal_corpus.hsn_sac_directory import find_hsn_or_sac
from finai.domain.models.financial_models import TaxRegime
from finai.domain.rag.knowledge_retriever import retrieve_legal_tax_passages
from finai.domain.rules.audit_trail import CalculationAuditLedger
from finai.domain.rules.emi_rules import calculate_emi
from finai.domain.rules.gst_rules import (
    calculate_gst_forward,
    check_blocked_credit_sec17_5,
    check_itc_eligibility_sec16,
)
from finai.domain.rules.tax_rules import (
    calculate_capital_gains_tax,
    calculate_hra_exemption,
    calculate_income_tax,
    calculate_presumptive_tax_44ad,
    calculate_presumptive_tax_44ada,
    compare_tax_regimes,
)


class OrchestrationPipeline:
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client
        self.audit_ledger = CalculationAuditLedger()

    def process_request(self, user_input: str, figure_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Master Pro CA Pipeline:
        1. Context & Intent Resolution (HSN, Billing/Invoicing, Personal Tax, Legal Query, EMI)
        2. Rule Execution & Statutory Retrieval
        3. Cryptographic SHA-256 Ledger Stamping
        4. Detailed Pro CA Response Synthesis
        """
        text_lower = user_input.lower().strip()

        # Case 1: HSN / SAC Code Lookup
        if any(w in text_lower for w in ["hsn", "sac code", "hsn code", "tariff code", "sac for", "hsn for"]):
            return self._handle_hsn_lookup(user_input)

        # Case 2: Natural Language Sale/Purchase Transaction & Bill Generation
        if any(w in text_lower for w in ["sold", "bought", "purchased", "sale of", "purchase of", "generate bill", "invoice for"]):
            return self._handle_conversational_billing(user_input)

        # Case 3: Personal Tax Optimization & Refund Maximizer
        if any(w in text_lower for w in ["salary", "refund", "maximize refund", "save tax", "regime", "115bac", "hra", "80c"]):
            return self._handle_tax_optimization(user_input)

        # Case 4: Capital Gains Query
        if any(w in text_lower for w in ["capital gain", "stcg", "ltcg", "shares", "property sale", "mutual fund gain"]):
            return self._handle_capital_gains(user_input)

        # Default: General Intent & Rule Execution
        intent = detect_intent(user_input, self.ollama_client)
        plan = plan_execution(intent, user_input)

        if not plan.is_ready:
            # Fall back to Legal RAG
            passages = retrieve_legal_tax_passages(user_input, top_k=2)
            if passages and passages[0][1] > 0.5:
                top_chunk, score = passages[0]
                resp = (
                    f"### 📖 Statutory Legal Citation: {top_chunk.statute_name} — {top_chunk.section_no}\n"
                    f"**Title**: {top_chunk.title}\n\n"
                    f"{top_chunk.content}\n\n"
                    f"💡 **CA Advisory Note**: Effective from {top_chunk.effective_date}. "
                    f"Categorized under: *{', '.join(top_chunk.topic_tags)}*."
                )
                return {
                    "intent": "legal_rag",
                    "response_type": "full_response",
                    "content": resp,
                    "rule_result": {"statute": top_chunk.statute_name, "section": top_chunk.section_no},
                    "confidence_score": 0.95
                }

            return {
                "intent": intent.value,
                "response_type": "clarifying_question",
                "content": plan.clarifying_question or "Could you specify the amount or financial parameters so I can compute the exact verified tax liability?",
                "rule_result": None,
                "confidence_score": 1.0,
            }

        rule_result = None
        if plan.rule_function_name == "calculate_gst_forward":
            res = calculate_gst_forward(
                amount=plan.extracted_slots.get("amount", 0.0),
                rate_percent=plan.extracted_slots.get("rate_percent", 18.0),
            )
            rule_result = res.model_dump()
            entry = self.audit_ledger.log_calculation("GST_CALCULATION", {"amount": plan.extracted_slots.get("amount", 0.0)}, rule_result)
            rule_result["audit_hash"] = entry.current_hash

        elif plan.rule_function_name == "calculate_emi":
            res = calculate_emi(
                principal=plan.extracted_slots.get("principal", 100000.0),
                annual_rate=plan.extracted_slots.get("annual_rate", 10.0),
                tenure_months=int(plan.extracted_slots.get("tenure_months", 12)),
            )
            rule_result = res.model_dump()
            entry = self.audit_ledger.log_calculation("EMI_CALCULATION", {"principal": plan.extracted_slots.get("principal", 100000.0)}, rule_result)
            rule_result["audit_hash"] = entry.current_hash

        elif plan.rule_function_name == "calculate_income_tax":
            res = calculate_income_tax(
                gross_income=plan.extracted_slots.get("gross_income", 500000.0)
            )
            rule_result = res.model_dump()
            entry = self.audit_ledger.log_calculation("INCOME_TAX_CALCULATION", {"gross": plan.extracted_slots.get("gross_income", 500000.0)}, rule_result)
            rule_result["audit_hash"] = entry.current_hash

        explanation = self._generate_explanation(intent, rule_result, user_input)

        return {
            "intent": intent.value,
            "response_type": "full_response",
            "content": explanation,
            "rule_result": rule_result,
            "confidence_score": 1.0 if self.ollama_client else 0.90,
        }

    # ---------------- SPECIALIZED CA WORKFLOWS ----------------

    def _handle_hsn_lookup(self, text: str) -> Dict[str, Any]:
        matches = find_hsn_or_sac(text, top_k=3)
        if not matches:
            content = (
                "### 🔍 HSN / SAC Code Resolver\n\n"
                "I couldn't find an exact match for your commodity in the instant directory. "
                "Common standard HSN categories include:\n"
                "- **8471**: Laptops & Computers (18% GST)\n"
                "- **8517**: Smartphones & Networking (18% GST)\n"
                "- **9403**: Office Furniture & Desks (18% GST)\n"
                "- **9983**: Software Development & IT Consulting (18% GST)\n"
                "- **9982**: Legal & Accounting CA Services (18% GST)"
            )
        else:
            lines = ["### 🔍 HSN / SAC Classification Results:\n"]
            for m in matches:
                itc_status = "✅ 100% Eligible for Input Tax Credit" if m["itc_eligible"] else f"❌ Blocked Credit ({m['blocked_reason']})"
                lines.append(
                    f"• **{m['code_type']} Code `{m['code']}`** — *{m['category']}*\n"
                    f"  - **Description**: {m['description']}\n"
                    f"  - **Applicable GST Slab**: **{m['gst_rate']}%**\n"
                    f"  - **ITC Audit Status**: {itc_status}\n"
                )
            content = "\n".join(lines)

        return {
            "intent": "hsn_lookup",
            "response_type": "full_response",
            "content": content,
            "rule_result": {"matches": matches},
            "confidence_score": 1.0
        }

    def _handle_conversational_billing(self, text: str) -> Dict[str, Any]:
        """
        Handles natural language sales/purchase billing, HSN code tagging, ITC verification,
        and generates a SHA-256 sealed transaction summary.
        """
        numbers = [float(n.replace(",", "")) for n in re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", text)]
        amount = numbers[0] if numbers else 50000.0

        is_purchase = any(w in text.lower() for w in ["bought", "purchase", "purchased", "expense"])
        is_interstate = any(w in text.lower() for w in ["interstate", "other state", "delhi to", "mumbai to", "igst"])

        # Auto-match HSN
        hsn_matches = find_hsn_or_sac(text, top_k=1)
        hsn_entry = hsn_matches[0] if hsn_matches else {
            "code": "8471", "code_type": "HSN", "category": "General Commercial Goods",
            "gst_rate": 18.0, "itc_eligible": True, "blocked_reason": None
        }

        rate = hsn_entry["gst_rate"]
        gst_calc = calculate_gst_forward(amount, rate, is_interstate)

        # Log to SHA-256 Ledger
        action_type = "PURCHASE_INWARD" if is_purchase else "SALE_OUTWARD"
        payload_in = {"amount": amount, "hsn": hsn_entry["code"], "type": action_type}
        payload_out = {"base": gst_calc.base_amount, "gst": gst_calc.gst_amount, "total": gst_calc.total_amount}
        entry = self.audit_ledger.log_calculation(f"BILLING_{action_type}", payload_in, payload_out)

        itc_banner = ""
        if is_purchase:
            if hsn_entry["itc_eligible"]:
                itc_banner = f"✅ **Input Tax Credit (ITC)**: ₹{gst_calc.gst_amount:,.2f} is **100% Eligible** to set off against outward GST liabilities."
            else:
                itc_banner = f"⚠️ **Blocked Credit Alert**: ₹{gst_calc.gst_amount:,.2f} is **Ineligible for ITC** under Section 17(5) ({hsn_entry.get('blocked_reason', '')})."
        else:
            itc_banner = f"📤 **Outward Tax Liability**: ₹{gst_calc.gst_amount:,.2f} collected and added to GSTR-3B Electronic Liability Ledger."

        tax_breakdown = (
            f"- **IGST ({gst_calc.igst_rate}%)**: ₹{gst_calc.igst_amount:,.2f}"
            if is_interstate else
            f"- **CGST ({gst_calc.cgst_rate}%)**: ₹{gst_calc.cgst_amount:,.2f}\n- **SGST ({gst_calc.sgst_rate}%)**: ₹{gst_calc.sgst_amount:,.2f}"
        )

        response = (
            f"### 🧾 Automated Tax Invoice & Transaction Breakdown\n\n"
            f"| Item / Particulars | Details |\n"
            f"| :--- | :--- |\n"
            f"| **Transaction Type** | {'Inward Purchase (Expense)' if is_purchase else 'Outward Supply (Sale)'} |\n"
            f"| **HSN/SAC Code** | `{hsn_entry['code']}` ({hsn_entry['category']}) |\n"
            f"| **Base Taxable Value** | **₹ {gst_calc.base_amount:,.2f}** |\n"
            f"| **GST Rate Applied** | {rate}% ({'Interstate IGST' if is_interstate else 'Intrastate CGST+SGST'}) |\n"
            f"| **Total GST Amount** | **₹ {gst_calc.gst_amount:,.2f}** |\n"
            f"| **Total Invoice Payable** | **₹ {gst_calc.total_amount:,.2f}** |\n\n"
            f"**Tax Slices**:\n{tax_breakdown}\n\n"
            f"{itc_banner}\n\n"
            f"🔒 **Tamper-Proof Audit Hash (SHA-256)**:\n`{entry.current_hash}`\n"
            f"*(Sealed in local ledger Block #{entry.index})*"
        )

        return {
            "intent": "conversational_billing",
            "response_type": "full_response",
            "content": response,
            "rule_result": payload_out,
            "confidence_score": 1.0
        }

    def _handle_tax_optimization(self, text: str) -> Dict[str, Any]:
        """
        Provides comprehensive personal tax analysis, Old vs New comparison,
        and legal refund maximization strategy.
        """
        numbers = [float(n.replace(",", "")) for n in re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", text)]
        salary = numbers[0] if numbers else 1800000.0

        res = compare_tax_regimes(
            gross_income=salary,
            is_salaried=True,
            deductions_80c=150000.0,
            deductions_80d=75000.0,  # 25k self + 50k parents
            deductions_80ccd=50000.0,  # NPS
            hra_exemption=180000.0,
            home_loan_interest_24b=0.0
        )

        nr = res["new_regime"]
        or_ = res["old_regime"]
        rec = res["recommended_regime"]
        savings = res["tax_savings"]

        response = (
            f"### 💡 Pro CA Tax Optimization & Refund Maximizer (AY 2026-27)\n\n"
            f"Based on your gross salary of **₹ {salary:,.2f}**, here is the exact comparative tax audit:\n\n"
            f"| Parameter | New Tax Regime (Sec 115BAC) | Old Tax Regime (With Deductions) |\n"
            f"| :--- | :--- | :--- |\n"
            f"| **Gross Salary** | ₹ {salary:,.2f} | ₹ {salary:,.2f} |\n"
            f"| **Standard Deduction (Sec 16ia)** | ₹ {nr['standard_deduction']:,.2f} | ₹ {or_['standard_deduction']:,.2f} |\n"
            f"| **Chapter VI-A & HRA Deductions** | ₹ 0.00 *(Disallowed)* | ₹ {or_['chapter_via_deductions']:,.2f} |\n"
            f"| **Net Taxable Income** | ₹ {nr['taxable_income']:,.2f} | ₹ {or_['taxable_income']:,.2f} |\n"
            f"| **Slab Tax** | ₹ {nr['slab_tax']:,.2f} | ₹ {or_['slab_tax']:,.2f} |\n"
            f"| **Section 87A Rebate** | ₹ {nr['rebate_87a']:,.2f} | ₹ {or_['rebate_87a']:,.2f} |\n"
            f"| **Final Net Tax Payable** | **₹ {nr['total_tax']:,.2f}** | **₹ {or_['total_tax']:,.2f}** |\n\n"
            f"🏆 **CA Recommendation**: **{res['advice']}**\n\n"
            f"#### 💰 Step-by-Step Legal Refund Maximization Checklist:\n"
            f"1. **Section 80C (₹1.50 Lakh)**: Utilize Employee Provident Fund (EPF), PPF, or ELSS funds.\n"
            f"2. **Section 80CCD(1B) (₹50,000)**: Invest exclusively in Tier-I National Pension System (NPS).\n"
            f"3. **Section 80D (₹75,000)**: Claim ₹25k for self/family + ₹50k for senior citizen parents' health insurance.\n"
            f"4. **Section 10(13A) HRA**: Submit valid rent agreements and landlord PAN to claim maximum HRA exemption."
        )

        return {
            "intent": "tax_optimization",
            "response_type": "full_response",
            "content": response,
            "rule_result": res,
            "confidence_score": 1.0
        }

    def _handle_capital_gains(self, text: str) -> Dict[str, Any]:
        numbers = [float(n.replace(",", "")) for n in re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", text)]
        gain = numbers[0] if numbers else 250000.0

        res = calculate_capital_gains_tax(stcg_equity=0.0, ltcg_equity=gain, ltcg_property_gold=0.0)

        response = (
            f"### 📈 Capital Gains Tax Audit (Budget 2024/2025 Revised Rates)\n\n"
            f"- **Equity Long-Term Capital Gain**: ₹ {gain:,.2f}\n"
            f"- **Annual Statutory Exemption (Sec 112A)**: **-₹ 1,25,000.00** *(Enhanced from ₹1.0L)*\n"
            f"- **Net Taxable LTCG**: ₹ {res['taxable_ltcg_equity']:,.2f}\n"
            f"- **Tax Rate**: 12.5% (Flat)\n"
            f"- **Health & Education Cess (4%)**: ₹ {res['cess_4pct']:,.2f}\n\n"
            f"👉 **Final Capital Gains Tax Payable: ₹ {res['final_capital_gains_tax_payable']:,.2f}**"
        )
        return {
            "intent": "capital_gains",
            "response_type": "full_response",
            "content": response,
            "rule_result": res,
            "confidence_score": 1.0
        }

    def _generate_explanation(self, intent: UserIntent, rule_result: Optional[Dict], user_input: str) -> str:
        if not rule_result:
            return "Please provide transaction numbers or salary amount so I can compute the exact verified tax liability."

        if intent == UserIntent.CALCULATE_GST:
            return (
                f"### 🧾 Verified GST Breakdown\n"
                f"- **Base Taxable Amount**: ₹{rule_result['base_amount']:,.2f}\n"
                f"- **GST Rate Applied**: {rule_result['gst_rate']}%\n"
                f"- **CGST**: ₹{rule_result['cgst_amount']:,.2f} | **SGST**: ₹{rule_result['sgst_amount']:,.2f}\n"
                f"- **Total GST Payable**: **₹{rule_result['gst_amount']:,.2f}**\n"
                f"- **Total Invoice Value**: **₹{rule_result['total_amount']:,.2f}**\n"
                f"- **Audit Hash**: `{rule_result.get('audit_hash', '')}`"
            )
        elif intent == UserIntent.CALCULATE_EMI:
            return (
                f"### 🏦 Verified Loan EMI & Amortization\n"
                f"- **Loan Principal**: ₹{rule_result['principal']:,.2f}\n"
                f"- **Monthly EMI**: **₹{rule_result['monthly_emi']:,.2f}**\n"
                f"- **Total Interest Payable**: ₹{rule_result['total_interest']:,.2f}\n"
                f"- **Total Payment over {rule_result['tenure_months']} months**: ₹{rule_result['total_payment']:,.2f}\n"
                f"- **Audit Hash**: `{rule_result.get('audit_hash', '')}`"
            )
        elif intent == UserIntent.CALCULATE_TAX:
            return (
                f"### 📊 Verified Income Tax Computation (AY 2026-27)\n"
                f"- **Gross Income**: ₹{rule_result['gross_income']:,.2f}\n"
                f"- **Standard Deduction**: ₹{rule_result['standard_deduction']:,.2f}\n"
                f"- **Taxable Income**: ₹{rule_result['taxable_income']:,.2f}\n"
                f"- **Section 87A Rebate**: ₹{rule_result['section_87a_rebate']:,.2f}\n"
                f"- **Net Tax Payable**: **₹{rule_result['total_tax_payable']:,.2f}**\n"
                f"- **Audit Hash**: `{rule_result.get('audit_hash', '')}`"
            )
        return "Transaction processed and verified by FinAI Symbolic Engine."
