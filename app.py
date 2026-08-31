from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from finai.catalog import CATALOG, by_code, DATASET_VERSION
from finai.gst_engine import resolve_rate
from finai.local_model import status as model_status
from finai.legal_sources import refresh as refresh_legal_sources, search as search_legal
from finai.parser import parse_transaction
from finai.rules import gst, income_tax, capital_gains, emi, hra_exemption, presumptive_44ada, presumptive_44ad, blocked_credit_17_5, rule_86b_check
from finai.storage import history, save
from finai.validators import validate_gst

st.set_page_config(page_title="FinAI — Offline CA Workspace", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #f6f8fc; color: #172033; font-family: "Segoe UI", Arial, sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #101a31; border-right: 0; }
    [data-testid="stSidebar"] * { color: #eef3ff; }
    [data-testid="stSidebar"] .stRadio label { border-radius: 10px; padding: .34rem .35rem; margin: .08rem 0; }
    .finai-brand { font-family: Georgia, serif; color: #fff; font-size: 2rem; margin: 0; }
    .finai-overline { color: #8ea6d9; font-size: .7rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
    .hero { background: radial-gradient(circle at 88% 5%, #445f9e 0, #172646 42%, #101a31 100%); color: #fff; border-radius: 24px; padding: 3.4rem 3rem; margin-bottom: 1.45rem; box-shadow: 0 20px 45px rgba(17,32,62,.18); }
    .hero h1 { font-family: Georgia, serif; font-size: clamp(2.35rem,4vw,4rem); margin: .2rem 0 .8rem; line-height: 1.06; }
    .hero p { color: #c9d6ef; max-width: 620px; font-size: 1.06rem; line-height: 1.55; }
    .section-title { font-family: Georgia, serif; font-size: 2rem; margin: .3rem 0; color: #172646; }
    .section-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1.3rem; }
    .premium-card { background: #fff; border: 1px solid #e4e9f2; padding: 1.45rem; border-radius: 18px; min-height: 222px; box-shadow: 0 8px 25px rgba(23,38,70,.055); }
    .premium-card h3 { margin: .55rem 0 .4rem; color: #162548; }
    .premium-card p { color: #62708b; line-height: 1.5; }
    .eyebrow { color: #4064ac; font-size: .72rem; letter-spacing: .11em; font-weight: 700; text-transform: uppercase; }
    .stButton > button { border-radius: 10px; border: 0; font-weight: 700; padding: .58rem .9rem; background: #183467; color: white; width: 100%; }
    .stButton > button:hover { background: #284d90; color: white; border: 0; }
    .stDownloadButton > button { border-radius: 10px; font-weight: 700; }
    [data-testid="stMetric"] { background: #fff; border: 1px solid #e5eaf3; border-radius: 14px; padding: .9rem; }
    .stTextArea textarea, .stTextInput input, .stNumberInput input { border-radius: 10px !important; border-color: #dbe2ef !important; background: #fff !important; }
    .trust-strip { display:flex; gap:1.4rem; flex-wrap:wrap; color:#73809a; font-size:.88rem; margin-top:1.4rem; }
    .status-pill { display:inline-block; background:#e7f6ee; color:#177047; border-radius:99px; padding:.32rem .7rem; font-size:.8rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

WORKSPACES = [
    "Home",
    "GST & Business",
    "Personal Tax",
    "Capital Gains",
    "Freelancer & MSME",
    "EMI Calculator",
    "Reconciliation",
    "Legal Knowledge",
    "Audit History",
]


def navigate(target: str) -> None:
    st.session_state.workspace = target


def rupees(amount: float) -> str:
    return f"₹{amount:,.2f}"


def sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="finai-overline">Private finance intelligence</div><div class="finai-brand">FinAI</div>', unsafe_allow_html=True)
        st.caption("Your offline CA workspace")
        st.divider()
        online, message = model_status()
        st.success(f"Local AI: {message}") if online else st.info(f"Local AI: {message}")
        st.caption("Your records and calculations remain on this computer.")
        st.divider()
        return st.radio("Workspace", WORKSPACES, key="workspace", label_visibility="collapsed")


def render_ca_explanation(kind: str, inputs: dict, result: dict, record: dict | None = None) -> None:
    """Render a human-readable, professional Chartered Accountant memorandum."""
    with st.expander("⚖️ CA Advisory Memorandum & Statutory Trace", expanded=True):
        if kind == "personal_tax":
            new_reg = result.get("new_regime", {})
            old_reg = result.get("old_regime", {})
            rec = result.get("recommendation", "New regime")
            diff = result.get("estimated_difference", 0.0)
            gross = inputs.get("gross_income", 0.0)
            
            st.markdown("### 📋 Income Tax Advisory Report (FY 2024-25 / AY 2025-26)")
            
            if rec == "New regime":
                st.success(f"**Optimal Strategy**: Select **New Tax Regime (Section 115BAC)** — Saves **{rupees(diff)}** in net taxes.")
            else:
                st.success(f"**Optimal Strategy**: Select **Old Tax Regime** — Saves **{rupees(diff)}** due to eligible Chapter VI-A deductions & home loan interest.")

            comp_df = pd.DataFrame({
                "Tax Component": [
                    "Gross Income / CTC",
                    "Standard Deduction (Sec 16(ia))",
                    "Chapter VI-A Deductions (80C/80D/NPS)",
                    "HRA Exemption (Sec 10(13A))",
                    "Home Loan Interest (Sec 24(b))",
                    "Net Taxable Income",
                    "Calculated Slab Tax",
                    "Section 87A Tax Rebate",
                    "Health & Education Cess (4%)",
                    "Total Net Tax Payable",
                ],
                "New Regime (Sec 115BAC)": [
                    rupees(gross),
                    rupees(new_reg.get("deductions_allowed", 75000)),
                    "Not Allowed",
                    "Not Allowed",
                    "Not Allowed",
                    rupees(new_reg.get("taxable_income", 0)),
                    rupees(new_reg.get("slab_tax", 0)),
                    rupees(new_reg.get("rebate", 0)),
                    rupees(new_reg.get("cess", 0)),
                    f"**{rupees(new_reg.get('total_tax', 0))}**",
                ],
                "Old Regime": [
                    rupees(gross),
                    "₹50,000.00",
                    rupees(inputs.get("deductions", 0)),
                    rupees(inputs.get("hra", 0)),
                    rupees(inputs.get("home_loan_interest", 0)),
                    rupees(old_reg.get("taxable_income", 0)),
                    rupees(old_reg.get("slab_tax", 0)),
                    rupees(old_reg.get("rebate", 0)),
                    rupees(old_reg.get("cess", 0)),
                    f"**{rupees(old_reg.get('total_tax', 0))}**",
                ],
            })
            st.table(comp_df)

            st.markdown("#### 📖 Statutory Basis & Legal Provisions:")
            st.markdown(f"""
1. **Section 115BAC (New Default Regime)**:
   - Enhanced Standard Deduction of **₹75,000** under Section 16(ia) (Finance Act 2024).
   - Revised Slabs: 0-4L (0%), 4-8L (5%), 8-12L (10%), 12-16L (15%), 16-20L (20%), 20-24L (25%), >24L (30%).
   - **Section 87A Rebate**: Resident individuals with taxable income up to **₹12,00,000** get full tax rebate (Effective Net Tax = ₹0).
2. **Old Tax Regime**:
   - Standard Deduction of **₹50,000** + Chapter VI-A deductions (80C, 80D, 80CCD, etc.) up to ₹3,00,000.
   - Slabs: 0-2.5L (0%), 2.5-5L (5%), 5-10L (20%), >10L (30%).
   - **Section 87A Rebate**: Applicable only up to **₹5,00,000** taxable income.
3. **Health & Education Cess**:
   - Flat **4%** statutory cess on aggregate income tax after Section 87A rebate.
            """)

        elif kind == "gst_transaction":
            cls = result.get("classification", {})
            st.markdown("### 📋 GST Compliance & Invoicing Assessment")
            st.markdown(f"""
- **Tariff Classification**: `{cls.get('code')}` — **{cls.get('name')}** ({cls.get('kind')})
- **Statutory Authority**: *{cls.get('source')}*
- **Taxable Base Amount**: {rupees(result.get('taxable_value', 0))}
- **Rate Applied**: **{result.get('rate')}%** ({result.get('tax_treatment')})
- **Tax Breakdown**: CGST: {rupees(result.get('cgst', 0))} | SGST: {rupees(result.get('sgst', 0))} | IGST: {rupees(result.get('igst', 0))}
- **Gross Invoice Total**: **{rupees(result.get('invoice_total', 0))}**
- **Input Tax Credit Status**: {result.get('itc_message')}
            """)
            val = validate_gst(result["taxable_value"], result["gst_amount"], result["cgst"], result["sgst"], result["igst"], result["invoice_total"], result["tax_treatment"] == "IGST")
            st.markdown("**Arithmetic Validation Checks:**")
            for check in val["checks"]:
                st.write(check)

        elif kind == "capital_gains":
            st.markdown("### 📋 Capital Gains Statutory Assessment (Budget 2024/25)")
            st.markdown(f"""
- **STCG Equity (Section 111A)**: Taxed @ **20%** = {rupees(result.get('stcg_tax', 0))}
- **LTCG Equity (Section 112A)**: Taxed @ **12.5%** after statutory exemption of **₹1,25,000** = {rupees(result.get('ltcg_equity_tax', 0))} (Exempt amount: {rupees(result.get('ltcg_equity_exemption', 0))})
- **LTCG Property / Gold (Section 112)**: Taxed @ **12.5%** (without indexation) = {rupees(result.get('ltcg_property_tax', 0))}
- **Health & Education Cess (4%)**: {rupees(result.get('cess', 0))}
- **Total Net Capital Gains Tax**: **{rupees(result.get('total_capital_gains_tax', 0))}**
            """)

        elif kind == "presumptive_tax":
            st.markdown("### 📋 Presumptive Taxation Advisory (Section 44ADA & 44AD)")
            ada = result.get("section_44ada", {})
            ad = result.get("section_44ad", {})
            st.markdown(f"""
- **Section 44ADA (Specified Professionals & Freelancers)**:
  - Gross Receipts: {rupees(ada.get('gross_receipts', 0))}
  - Statutory Deemed Taxable Profit (50%): **{rupees(ada.get('taxable_profit', 0))}** *(No books of accounts/audit required up to ₹75 Lakhs)*.
- **Section 44AD (Small Businesses & Traders)**:
  - Digital Turnover (6% Deemed Profit): {rupees(ad.get('digital_turnover', 0))} → Profit: {rupees(ad.get('digital_profit', 0))}
  - Cash Turnover (8% Deemed Profit): {rupees(ad.get('cash_turnover', 0))} → Profit: {rupees(ad.get('cash_profit', 0))}
  - Total Deemed Business Profit: **{rupees(ad.get('total_profit', 0))}**
            """)

        elif kind == "emi_calculation":
            st.markdown("### 📋 Loan Amortization & Repayment Summary")
            st.markdown(f"""
- **Loan Principal**: {rupees(result.get('principal', 0))}
- **Interest Rate**: {result.get('annual_rate')}% p.a. (Reducing Balance Method)
- **Tenure**: {result.get('tenure_months')} Months ({result.get('tenure_months', 0) // 12} Years {result.get('tenure_months', 0) % 12} Months)
- **Equated Monthly Installment (EMI)**: **{rupees(result.get('monthly_emi', 0))}**
- **Total Lifetime Interest Burden**: {rupees(result.get('total_interest', 0))}
- **Total Repayment Amount**: **{rupees(result.get('total_payment', 0))}**
            """)

        if record:
            st.divider()
            with st.expander("🔒 Cryptographic SHA-256 Audit Trail", expanded=False):
                st.caption("Immutable ledger entry details for audit defense and compliance verification.")
                b_hash = record.get('hash') or record.get('audit_hash', '')
                st.code(f"Audit Record ID : #{record.get('id')}\nTimestamp       : {record.get('created_at')}\nPrevious Hash   : {record.get('previous_hash')}\nBlock Hash      : {b_hash}", language="text")


def audit_panel(kind: str, record: dict, inputs: dict, result: dict) -> None:
    st.success(f"Saved locally as audit record #{record['id']}")
    render_ca_explanation(kind, inputs, result, record)


def why_this_answer(item: dict, rate_result, result: dict, is_interstate: bool) -> None:
    """Render a detailed Why This Answer expander with statutory citations."""
    with st.expander("💡 Why this answer? — statutory verification", expanded=False):
        st.markdown(f"""
| Audit Field | Value |
|:---|:---|
| **HSN/SAC Code** | `{item['code']}` ({item['kind']}) |
| **Classification** | {item['name']} |
| **Statutory Source** | {item['source']} |
| **Effective From** | {item.get('effective_from', '2017-07-01')} |
| **Dataset Version** | {DATASET_VERSION} |
| **GST Rate Applied** | {item['rate']}% |
| **Place of Supply** | {'Interstate (IGST)' if is_interstate else 'Intrastate (CGST + SGST)'} |
| **ITC Status** | {'Eligible subject to Section 16 conditions' if item['itc'] else 'Potentially blocked — ' + item.get('blocked_reason', 'review before claim')} |
| **Calculation** | ₹{result['taxable_value']:,.2f} × {item['rate']}% = ₹{result['gst_amount']:,.2f} |
| **Invoice Total** | ₹{result['taxable_value']:,.2f} + ₹{result['gst_amount']:,.2f} = ₹{result['invoice_total']:,.2f} |
        """)
        val = validate_gst(result["taxable_value"], result["gst_amount"], result["cgst"], result["sgst"], result["igst"], result["invoice_total"], is_interstate)
        for check in val["checks"]:
            st.write(check)


# ==================== WORKSPACES ====================

def home_workspace() -> None:
    st.markdown("""
    <div class="hero">
      <div class="finai-overline">Offline-first. Explainable. Local.</div>
      <h1>Your private CA<br/>workspace.</h1>
      <p>Move from natural-language input to a verified financial result—without sending your records to a cloud AI service.</p>
      <div class="trust-strip"><span>● Deterministic calculations</span><span>● SHA-256 audit chain</span><span>● Optional local AI</span><span>● Date-aware GST rates</span></div>
    </div>
    <div class="section-title">What would you like to do?</div>
    <div class="section-subtitle">Choose a focused workspace to start. Every action is saved only after your confirmation.</div>
    """, unsafe_allow_html=True)
    a, b, c = st.columns(3, gap="large")
    with a:
        st.markdown('<div class="premium-card"><div class="eyebrow">GST & business</div><h3>Record a transaction</h3><p>Classify goods or services, apply the right GST treatment, inspect ITC, and save the audit trail.</p></div>', unsafe_allow_html=True)
        st.button("Open GST desk →", key="go_gst", on_click=navigate, args=("GST & Business",))
    with b:
        st.markdown('<div class="premium-card"><div class="eyebrow">Personal tax</div><h3>Compare tax regimes</h3><p>Enter your actual income and deductions to see an explainable old-vs-new regime comparison.</p></div>', unsafe_allow_html=True)
        st.button("Open tax desk →", key="go_tax", on_click=navigate, args=("Personal Tax",))
    with c:
        st.markdown('<div class="premium-card"><div class="eyebrow">Capital gains</div><h3>Compute gains tax</h3><p>Budget 2024/25 revised STCG (20%) and LTCG (12.5%) rates with ₹1.25L exemption.</p></div>', unsafe_allow_html=True)
        st.button("Open capital gains →", key="go_cg", on_click=navigate, args=("Capital Gains",))
    st.markdown("<br/>", unsafe_allow_html=True)
    d, e, f = st.columns(3, gap="large")
    with d:
        st.markdown('<div class="premium-card"><div class="eyebrow">Freelancer & MSME</div><h3>Presumptive tax</h3><p>Section 44ADA for professionals and 44AD for small businesses with deemed profit rates.</p></div>', unsafe_allow_html=True)
        st.button("Open presumptive tax →", key="go_pt", on_click=navigate, args=("Freelancer & MSME",))
    with e:
        st.markdown('<div class="premium-card"><div class="eyebrow">Loans</div><h3>EMI calculator</h3><p>Standard reducing-balance EMI for home loans, car loans, or personal loans.</p></div>', unsafe_allow_html=True)
        st.button("Open EMI calculator →", key="go_emi", on_click=navigate, args=("EMI Calculator",))
    with f:
        st.markdown('<div class="premium-card"><div class="eyebrow">Compliance</div><h3>Reconcile ITC</h3><p>Upload a purchase register and GSTR-2B export, then see the matched and missing invoices.</p></div>', unsafe_allow_html=True)
        st.button("Open reconciliation →", key="go_recon", on_click=navigate, args=("Reconciliation",))
    st.markdown("<br/>", unsafe_allow_html=True)
    x, y = st.columns(2)
    x.button("Search offline legal knowledge", key="go_legal", on_click=navigate, args=("Legal Knowledge",))
    y.button("View saved audit records", key="go_audit", on_click=navigate, args=("Audit History",))
    st.caption("For education and demo use. Verify current legislation, notifications, and filing schemas before acting on an output.")


def gst_workspace() -> None:
    st.markdown('<div class="eyebrow">Business compliance</div><div class="section-title">GST & Business desk</div><div class="section-subtitle">Draft a transaction in plain English, verify the facts, then save a complete local audit record.</div>', unsafe_allow_html=True)
    text = st.text_area("Describe the transaction", placeholder="Example: I sold 5 office chairs for ₹45,000 to a customer in Mumbai.", height=110)
    if text:
        draft = parse_transaction(text)
        st.session_state.gst_draft = draft
    draft = st.session_state.get("gst_draft")
    if not draft:
        st.info("Start by describing a sale or purchase, or use the guided form below.")
        draft = {"raw": "", "amount": None, "transaction_type": "sale", "interstate": False, "candidates": [], "needs_classification": False, "quick_picks": []}

    # Smart clarification when product unspecified
    if draft.get("needs_classification") and draft.get("quick_picks"):
        st.warning(f"I detected a transaction amount of **{rupees(draft['amount'])}**, but I need to know what was {'purchased' if draft['transaction_type'] == 'purchase' else 'sold'} to determine the correct GST rate.")
        st.write("**Quick picks — select a category:**")
        cols = st.columns(4)
        for i, pick in enumerate(draft["quick_picks"]):
            with cols[i % 4]:
                if st.button(pick["label"], key=f"qp_{i}"):
                    item = by_code(pick["code"])
                    if item:
                        draft["candidates"] = [item]
                        draft["needs_classification"] = False
                        st.session_state.gst_draft = draft
                        st.rerun()

    left, right = st.columns(2)
    with left:
        amount = st.number_input("Taxable value, before GST", min_value=0.0, value=float(draft["amount"] or 0.0), step=1000.0)
        kind = st.selectbox("Transaction type", ["sale", "purchase"], index=0 if draft["transaction_type"] == "sale" else 1)
        interstate = st.toggle("Interstate supply (IGST)", value=draft["interstate"], help="Keep this off for intrastate CGST + SGST.")
    with right:
        candidates = draft["candidates"] or CATALOG
        options = {f"{item['kind']} {item['code']} — {item['name']} ({item['rate']}%)": item["code"] for item in candidates}
        selected_label = st.selectbox("Verified HSN/SAC candidate", list(options))
        item = by_code(options[selected_label])
        st.caption(item["source"])
        itc_msg = "Eligible subject to Section 16 conditions" if item["itc"] else f"Review: {item.get('blocked_reason', 'credit may be blocked / conditional')}"
        st.write("ITC status:", itc_msg)
        if item.get("rcm_applicable"):
            st.warning("⚠️ Reverse Charge Mechanism (RCM) may apply to this service.")

    # Section 17(5) blocked credit check for purchases
    if kind == "purchase" and not item["itc"]:
        st.error(f"🚫 **Blocked Credit**: GST paid on this purchase is ineligible for Input Tax Credit under {item.get('blocked_reason', 'Section 17(5)')}.")

    missing = []
    if amount <= 0:
        missing.append("taxable value")
    if missing:
        st.warning("I need " + ", ".join(missing) + " before I can calculate.")
        return

    result = gst(amount, item["rate"], interstate)
    result.update({
        "classification": {key: item[key] for key in ("code", "kind", "name", "source")},
        "tax_treatment": "IGST" if interstate else "CGST + SGST",
        "itc_message": itc_msg,
    })

    st.markdown("<div class='section-title' style='font-size:1.45rem'>Verified transaction draft</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Taxable value", rupees(result["taxable_value"]))
    c2.metric("GST", rupees(result["gst_amount"]))
    c3.metric("Tax treatment", result["tax_treatment"])
    c4.metric("Invoice total", rupees(result["invoice_total"]))
    st.caption(result["itc_message"])

    # Why This Answer
    why_this_answer(item, None, result, interstate)

    if st.button("Confirm and save transaction", type="primary"):
        inputs = {"description": draft["raw"], "amount": amount, "transaction_type": kind, "interstate": interstate, "classification": item["code"]}
        record = save("gst_transaction", inputs, result)
        audit_panel("gst_transaction", record, inputs, result)
        st.download_button("Download transaction JSON", json.dumps({"input": inputs, "result": result, "audit": record}, indent=2), "finai_gst_draft.json", "application/json")


def tax_workspace() -> None:
    st.markdown('<div class="eyebrow">Individual planning</div><div class="section-title">Personal tax desk</div><div class="section-subtitle">Compare regimes using only the amounts you enter. FinAI never invents investments or exemptions.</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        gross = st.number_input("Annual gross income", min_value=0.0, value=1200000.0, step=25000.0)
        deductions = st.number_input("Old-regime deductions (80C / 80D / NPS total)", min_value=0.0, value=0.0, step=10000.0)
    with right:
        hra = st.number_input("Eligible HRA exemption", min_value=0.0, value=0.0, step=10000.0)
        home = st.number_input("Eligible home-loan interest", min_value=0.0, value=0.0, step=10000.0)

    # HRA calculator
    with st.expander("🏠 Calculate HRA exemption"):
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            basic = st.number_input("Basic salary (annual)", min_value=0.0, value=600000.0, step=25000.0, key="hra_basic")
            hra_rec = st.number_input("Actual HRA received (annual)", min_value=0.0, value=240000.0, step=10000.0, key="hra_rec")
        with hcol2:
            rent = st.number_input("Annual rent paid", min_value=0.0, value=240000.0, step=10000.0, key="hra_rent")
            metro = st.checkbox("Metro city (50% of basic)", value=True, key="hra_metro")
        hra_res = hra_exemption(basic, hra_rec, rent, metro)
        st.success(f"**HRA exempt**: {rupees(hra_res['exempt_hra'])} | **Taxable HRA**: {rupees(hra_res['taxable_hra'])}")
        st.caption(f"Minimum of: Actual HRA ({rupees(hra_res['actual_hra'])}), {'50' if metro else '40'}% of basic ({rupees(hra_res['percent_of_basic'])}), Rent - 10% basic ({rupees(hra_res['rent_minus_10pct'])})")

    new = income_tax(gross, "new")
    old = income_tax(gross, "old", deductions, hra, home)
    winner = "New regime" if new["total_tax"] <= old["total_tax"] else "Old regime"
    savings = abs(new["total_tax"] - old["total_tax"])
    st.markdown("<div class='section-title' style='font-size:1.45rem'>Regime comparison</div>", unsafe_allow_html=True)
    table = pd.DataFrame([new, old]).set_index("regime")[["deductions_allowed", "taxable_income", "slab_tax", "rebate", "cess", "total_tax"]]
    st.dataframe(table.style.format(rupees), use_container_width=True)
    st.success(f"Based on the numbers entered, **{winner}** is lower by **{rupees(savings)}**.")

    inputs = {"gross_income": gross, "deductions": deductions, "hra": hra, "home_loan_interest": home}
    result = {"new_regime": new, "old_regime": old, "recommendation": winner, "estimated_difference": savings}
    
    # Render rich CA advisory report
    render_ca_explanation("personal_tax", inputs, result)

    if st.button("Save personal-tax calculation", type="primary"):
        record = save("personal_tax", inputs, result)
        audit_panel("personal_tax", record, inputs, result)


def capital_gains_workspace() -> None:
    st.markdown('<div class="eyebrow">Investment taxation</div><div class="section-title">Capital gains tax (Budget 2024/25)</div><div class="section-subtitle">Revised rates effective from 23 July 2024. LTCG equity at 12.5% with ₹1.25L exemption. STCG equity at 20%.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        stcg_eq = st.number_input("STCG — equity / mutual funds (Section 111A) [20%]", min_value=0.0, value=50000.0, step=10000.0)
        ltcg_eq = st.number_input("LTCG — equity / mutual funds (Section 112A) [12.5%]", min_value=0.0, value=250000.0, step=10000.0)
    with c2:
        ltcg_prop = st.number_input("LTCG — property / gold / other (Section 112) [12.5%]", min_value=0.0, value=0.0, step=50000.0)

    res = capital_gains(stcg_eq, ltcg_eq, ltcg_prop)
    st.markdown("<div class='section-title' style='font-size:1.45rem'>Capital gains tax breakdown</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("STCG tax (20%)", rupees(res["stcg_tax"]))
    c2.metric("LTCG equity tax (12.5%)", rupees(res["ltcg_equity_tax"]))
    c3.metric("LTCG property tax (12.5%)", rupees(res["ltcg_property_tax"]))
    st.info(f"Statutory exemption under Section 112A: **-{rupees(res['ltcg_equity_exemption'])}** applied to equity LTCG.")
    st.success(f"**Total capital gains tax (with 4% cess): {rupees(res['total_capital_gains_tax'])}**")

    inputs = {"stcg_equity": stcg_eq, "ltcg_equity": ltcg_eq, "ltcg_property": ltcg_prop}
    render_ca_explanation("capital_gains", inputs, res)

    if st.button("Save capital gains calculation", type="primary"):
        record = save("capital_gains", inputs, res)
        audit_panel("capital_gains", record, inputs, res)


def freelancer_workspace() -> None:
    st.markdown('<div class="eyebrow">Small business & freelancers</div><div class="section-title">Presumptive taxation (44ADA & 44AD)</div><div class="section-subtitle">Simplified tax for professionals and small businesses with deemed profit rates.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Section 44ADA — Professionals / Freelancers")
        st.caption("Doctors, lawyers, CAs, architects, engineers, interior decorators, and other specified professionals.")
        p_rec = st.number_input("Gross professional receipts", min_value=0.0, max_value=7500000.0, value=3500000.0, step=50000.0)
        res_ada = presumptive_44ada(p_rec)
        st.success(f"**Deemed taxable profit (50%)**: {rupees(res_ada['taxable_profit'])}")
    with c2:
        st.markdown("#### Section 44AD — Small Businesses")
        st.caption("Any eligible business (not professionals) with turnover up to ₹3 crore.")
        d_to = st.number_input("Digital turnover (6% profit rate)", min_value=0.0, value=8000000.0, step=100000.0)
        c_to = st.number_input("Cash turnover (8% profit rate)", min_value=0.0, value=1000000.0, step=100000.0)
        res_ad = presumptive_44ad(d_to, c_to)
        st.success(f"**Total deemed profit**: {rupees(res_ad['total_profit'])}")
        st.caption(f"Digital: {rupees(res_ad['digital_profit'])} + Cash: {rupees(res_ad['cash_profit'])}")

    inputs = {"type": "44ADA+44AD", "professional_receipts": p_rec, "digital_turnover": d_to, "cash_turnover": c_to}
    result = {"section_44ada": res_ada, "section_44ad": res_ad}
    render_ca_explanation("presumptive_tax", inputs, result)

    if st.button("Save presumptive tax calculation", type="primary"):
        record = save("presumptive_tax", inputs, result)
        audit_panel("presumptive_tax", record, inputs, result)


def emi_workspace() -> None:
    st.markdown('<div class="eyebrow">Loan planning</div><div class="section-title">EMI calculator</div><div class="section-subtitle">Standard reducing-balance EMI for any loan type.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        principal = st.number_input("Loan principal (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    with c2:
        rate = st.number_input("Annual interest rate (%)", min_value=0.0, max_value=30.0, value=8.5, step=0.25)
    with c3:
        tenure = st.number_input("Tenure (months)", min_value=1, max_value=360, value=240, step=12)

    res = emi(principal, rate, tenure)
    st.markdown("<div class='section-title' style='font-size:1.45rem'>Repayment summary</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly EMI", rupees(res["monthly_emi"]))
    c2.metric("Total interest", rupees(res["total_interest"]))
    c3.metric("Total payment", rupees(res["total_payment"]))
    st.caption(f"Loan: {rupees(res['principal'])} at {res['annual_rate']}% for {res['tenure_months']} months ({res['tenure_months'] // 12} years {res['tenure_months'] % 12} months)")

    inputs = {"principal": principal, "annual_rate": rate, "tenure_months": tenure}
    render_ca_explanation("emi_calculation", inputs, res)

    if st.button("Save EMI calculation", type="primary"):
        record = save("emi_calculation", inputs, res)
        audit_panel("emi_calculation", record, inputs, res)


def reconciliation_workspace() -> None:
    st.markdown('<div class="eyebrow">Input tax credit</div><div class="section-title">GSTR-2B reconciliation</div><div class="section-subtitle">Upload your purchase register and GSTR-2B export to identify matched and missing invoices.</div>', unsafe_allow_html=True)
    pcol, bcol = st.columns(2)
    purchase_file = pcol.file_uploader("Purchase register CSV", type="csv")
    gstr_file = bcol.file_uploader("GSTR-2B CSV", type="csv")
    if purchase_file and gstr_file:
        purchases, two_b = pd.read_csv(purchase_file), pd.read_csv(gstr_file)
        required = {"invoice_no", "tax_amount"}
        if not required.issubset(purchases.columns) or not required.issubset(two_b.columns):
            st.error("Both files need `invoice_no` and `tax_amount` columns.")
            return
        merged = purchases.merge(two_b[["invoice_no", "tax_amount"]], on="invoice_no", how="left", suffixes=("_purchase", "_2b"))
        merged["status"] = merged["tax_amount_2b"].notna().map({True: "Matched", False: "Missing in GSTR-2B"})

        # Section 17(5) blocked credit check
        if "category" in merged.columns:
            blocked_flags = merged["category"].apply(lambda c: blocked_credit_17_5(str(c)) if pd.notna(c) else {"is_blocked": False})
            merged["itc_blocked"] = blocked_flags.apply(lambda x: x["is_blocked"])
            merged["block_reason"] = blocked_flags.apply(lambda x: x.get("reason", ""))

        matched_itc = float(merged.loc[merged.status == "Matched", "tax_amount_purchase"].sum())
        missing_count = int((merged.status == "Missing in GSTR-2B").sum())
        c1, c2 = st.columns(2)
        c1.metric("Eligible matched ITC", rupees(matched_itc))
        c2.metric("Missing in GSTR-2B", missing_count)
        st.dataframe(merged, use_container_width=True)
        st.download_button("Download reconciliation CSV", merged.to_csv(index=False), "finai_reconciliation.csv", "text/csv")


def legal_workspace() -> None:
    st.markdown('<div class="eyebrow">Statutory research</div><div class="section-title">Legal knowledge</div><div class="section-subtitle">Refresh official sources when online. After they are indexed, your searches work from the local database.</div>', unsafe_allow_html=True)
    if st.button("Refresh from official sources"):
        with st.spinner("Downloading and indexing official-source material locally…"):
            count, errors = refresh_legal_sources()
        st.success(f"Indexed {count} official sources locally.")
        for error in errors:
            st.warning(error)
    query = st.text_input("Search downloaded GST / income-tax material")
    if query:
        matches = search_legal(query)
        if not matches:
            st.info("No local result yet. Connect to the internet and refresh the official-source knowledge base first.")
        for match in matches:
            st.markdown(f"**[{match['title']}]({match['url']})**")
            st.caption(f"Fetched {match['fetched_at']} · {match['topic']}")
            st.write(match["snippet"].replace("[[", "**").replace("]]", "**"))


def audit_workspace() -> None:
    st.markdown('<div class="eyebrow">Traceability</div><div class="section-title">Local audit history</div><div class="section-subtitle">Every saved record contains its inputs, calculation output, and a SHA-256 chain reference.</div>', unsafe_allow_html=True)
    records = history()
    if not records:
        st.info("No records saved yet.")
        return
    for row in records:
        with st.expander(f"#{row['id']} · {row['kind']} · {row['created_at']}"):
            render_ca_explanation(row['kind'], json.loads(row['input_json']), json.loads(row['result_json']), dict(row))


# ==================== ROUTING ====================

workspace = sidebar()
if workspace == "Home":
    home_workspace()
elif workspace == "GST & Business":
    gst_workspace()
elif workspace == "Personal Tax":
    tax_workspace()
elif workspace == "Capital Gains":
    capital_gains_workspace()
elif workspace == "Freelancer & MSME":
    freelancer_workspace()
elif workspace == "EMI Calculator":
    emi_workspace()
elif workspace == "Reconciliation":
    reconciliation_workspace()
elif workspace == "Legal Knowledge":
    legal_workspace()
else:
    audit_workspace()
