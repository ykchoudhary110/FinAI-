from __future__ import annotations

import json
import urllib.request
import urllib.error

import pandas as pd
import streamlit as st

from finai.catalog import CATALOG, by_code, find_candidates, DATASET_VERSION
from finai.gst_engine import resolve_rate
from finai.local_model import status as model_status
from finai.legal_sources import refresh as refresh_legal_sources, search as search_legal
from finai.parser import parse_transaction
from finai.rules import (
    gst, income_tax, capital_gains, emi, hra_exemption,
    presumptive_44ada, presumptive_44ad, blocked_credit_17_5, rule_86b_check,
)
from finai.storage import history, save
from finai.validators import validate_gst

st.set_page_config(page_title="FinAI — CA Pro", page_icon="⚖️", layout="wide")

# ==================== STYLING ====================

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
    .hero h1 { font-family: Georgia, serif; font-size: clamp(2.35rem,4vw,3.5rem); margin: .2rem 0 .8rem; line-height: 1.06; }
    .hero p { color: #c9d6ef; max-width: 620px; font-size: 1.06rem; line-height: 1.55; }
    .section-title { font-family: Georgia, serif; font-size: 2rem; margin: .3rem 0; color: #172646; }
    .section-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1.3rem; }
    .premium-card { background: #fff; border: 1px solid #e4e9f2; padding: 1.45rem; border-radius: 18px; min-height: 180px; box-shadow: 0 8px 25px rgba(23,38,70,.055); }
    .premium-card h3 { margin: .55rem 0 .4rem; color: #162548; }
    .premium-card p { color: #62708b; line-height: 1.5; }
    .eyebrow { color: #4064ac; font-size: .72rem; letter-spacing: .11em; font-weight: 700; text-transform: uppercase; }
    .stButton > button { border-radius: 10px; border: 0; font-weight: 700; padding: .58rem .9rem; background: #183467; color: white; width: 100%; }
    .stButton > button:hover { background: #284d90; color: white; border: 0; }
    .stDownloadButton > button { border-radius: 10px; font-weight: 700; }
    [data-testid="stMetric"] { background: #fff; border: 1px solid #e5eaf3; border-radius: 14px; padding: .9rem; }
    .stTextArea textarea, .stTextInput input, .stNumberInput input { border-radius: 10px !important; border-color: #dbe2ef !important; background: #fff !important; }
    .trust-strip { display:flex; gap:1.4rem; flex-wrap:wrap; color:#73809a; font-size:.88rem; margin-top:1.4rem; }
    .advice-box { background: #fff; border: 1px solid #d0ddf0; border-radius: 16px; padding: 1.6rem; margin: .6rem 0; }
    .advice-box h4 { color: #172646; margin: 0 0 .5rem; }
    .risk-flag { background: #fff4f4; border: 1px solid #fcd0d0; border-radius: 12px; padding: 1rem 1.2rem; margin: .4rem 0; }
    .risk-flag p { margin: 0; color: #9b2c2c; }
    .saving-flag { background: #f0faf4; border: 1px solid #b7e6ca; border-radius: 12px; padding: 1rem 1.2rem; margin: .4rem 0; }
    .saving-flag p { margin: 0; color: #1a6b3e; }
    .ca-chat-msg { background: #fff; border: 1px solid #e4e9f2; border-radius: 14px; padding: 1.1rem 1.3rem; margin: .5rem 0; }
    .ca-chat-user { background: #eef3ff; border: 1px solid #d0ddf0; border-radius: 14px; padding: 1.1rem 1.3rem; margin: .5rem 0; text-align: right; }
</style>
""", unsafe_allow_html=True)

WORKSPACES = [
    "🏠 Home",
    "💬 CA Copilot",
    "📊 GST Desk",
    "📋 Income Tax",
    "📈 Capital Gains",
    "🏢 Freelancer / MSME",
    "🏦 EMI Calculator",
    "🔍 Reconciliation",
    "📚 Legal Knowledge",
    "📜 Audit History",
]


def navigate(target: str) -> None:
    st.session_state.workspace = target


def rupees(amount: float) -> str:
    return f"₹{amount:,.2f}"


# ==================== SIDEBAR ====================

def sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="finai-overline">Private finance intelligence</div><div class="finai-brand">FinAI — CA Pro</div>', unsafe_allow_html=True)
        st.caption("Your offline Chartered Accountant")
        st.divider()
        online, message = model_status()
        if online:
            st.success(f"🟢 {message}")
        else:
            st.info(f"⚪ Deterministic mode active")
        st.caption("All data stays on this computer.")
        st.divider()
        return st.radio("Workspace", WORKSPACES, key="workspace", label_visibility="collapsed")


# ==================== OLLAMA CHAT ====================

def ollama_generate(prompt: str, system: str = "") -> str | None:
    """Call local Ollama model. Returns None if unavailable."""
    try:
        payload = json.dumps({
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "system": system,
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp).get("response", "")
    except Exception:
        return None


CA_SYSTEM_PROMPT = """You are FinAI CA Pro, an expert Indian Chartered Accountant AI assistant.
You provide tax planning advice, GST compliance guidance, and financial advisory for Indian individuals and businesses.

CRITICAL RULES:
1. You NEVER perform calculations yourself. When the user describes a financial scenario, you analyze it qualitatively and explain which tax provisions, sections, and strategies apply.
2. The actual calculations are done by the deterministic engine — you only interpret and advise.
3. Always cite specific sections of Indian tax law (Income Tax Act 1961, CGST Act 2017, Finance Act amendments).
4. Be concise but thorough. Use bullet points.
5. If you don't know something, say so. Never fabricate tax rates or legal provisions.
6. Respond in a professional but approachable tone, like a trusted CA advisor.
"""


# ==================== CA CONSULTATION (GUIDED) ====================

def run_consultation(profile: str, gross: float, gst_turnover: float,
                     is_interstate: bool, deductions: float, hra: float,
                     home_loan: float, stcg: float, ltcg_eq: float,
                     ltcg_prop: float, has_car: bool, has_food_expenses: bool,
                     digital_pct: float) -> dict:
    """Run ALL engines and produce a unified CA advisory."""
    report = {"sections": [], "risks": [], "savings": [], "numbers": {}}

    # 1. Income Tax
    new = income_tax(gross, "new")
    old = income_tax(gross, "old", deductions, hra, home_loan)
    winner = "New regime" if new["total_tax"] <= old["total_tax"] else "Old regime"
    tax_saved = abs(new["total_tax"] - old["total_tax"])
    report["numbers"]["income_tax"] = {"new": new, "old": old, "winner": winner, "saved": tax_saved}
    report["sections"].append({
        "title": "Income Tax — Regime Comparison (FY 2024-25)",
        "content": f"On gross income of {rupees(gross)}, **{winner}** saves you **{rupees(tax_saved)}**.\n\n"
                   f"| | New Regime (Sec 115BAC) | Old Regime |\n|:--|:--|:--|\n"
                   f"| Standard Deduction | {rupees(new['deductions_allowed'])} | ₹50,000 + deductions |\n"
                   f"| Taxable Income | {rupees(new['taxable_income'])} | {rupees(old['taxable_income'])} |\n"
                   f"| Slab Tax | {rupees(new['slab_tax'])} | {rupees(old['slab_tax'])} |\n"
                   f"| Sec 87A Rebate | {rupees(new['rebate'])} | {rupees(old['rebate'])} |\n"
                   f"| Cess (4%) | {rupees(new['cess'])} | {rupees(old['cess'])} |\n"
                   f"| **Net Tax** | **{rupees(new['total_tax'])}** | **{rupees(old['total_tax'])}** |"
    })
    if tax_saved > 0:
        report["savings"].append(f"Switch to **{winner}** — saves **{rupees(tax_saved)}** per year (Section {'115BAC' if winner == 'New regime' else '87A + Ch VI-A'})")

    # New regime rebate advisory
    if new["taxable_income"] <= 1200000 and new["total_tax"] == 0:
        report["savings"].append(f"Under New Regime, your taxable income {rupees(new['taxable_income'])} qualifies for **full Section 87A rebate** — effectively zero income tax")

    # 2. Capital Gains (only if non-zero)
    if stcg > 0 or ltcg_eq > 0 or ltcg_prop > 0:
        cg = capital_gains(stcg, ltcg_eq, ltcg_prop)
        report["numbers"]["capital_gains"] = cg
        report["sections"].append({
            "title": "Capital Gains Tax (Budget 2024/25 Rates)",
            "content": f"| Component | Amount |\n|:--|:--|\n"
                       f"| STCG Equity @ 20% (Sec 111A) | {rupees(cg['stcg_tax'])} |\n"
                       f"| LTCG Equity Exemption (Sec 112A) | −{rupees(cg['ltcg_equity_exemption'])} |\n"
                       f"| LTCG Equity @ 12.5% | {rupees(cg['ltcg_equity_tax'])} |\n"
                       f"| LTCG Property @ 12.5% (Sec 112) | {rupees(cg['ltcg_property_tax'])} |\n"
                       f"| Cess (4%) | {rupees(cg['cess'])} |\n"
                       f"| **Total CG Tax** | **{rupees(cg['total_capital_gains_tax'])}** |"
        })
        if cg['ltcg_equity_exemption'] > 0:
            report["savings"].append(f"LTCG equity exemption of **{rupees(cg['ltcg_equity_exemption'])}** applied under Section 112A (Budget 2024/25)")

    # 3. GST / Presumptive (only if turnover > 0)
    if gst_turnover > 0:
        if profile == "Freelancer / Professional":
            ada = presumptive_44ada(gst_turnover)
            report["numbers"]["presumptive"] = ada
            report["sections"].append({
                "title": "Presumptive Taxation — Section 44ADA (Professionals)",
                "content": f"Gross receipts: {rupees(gst_turnover)}\n\n"
                           f"Deemed taxable profit (50%): **{rupees(ada['taxable_profit'])}**\n\n"
                           f"No books of accounts or tax audit required up to ₹75 Lakhs.\n\n"
                           f"*If gross receipts exceed ₹20 Lakhs, GST registration is mandatory.*"
            })
            if gst_turnover <= 7500000:
                report["savings"].append(f"Section 44ADA: Only **50%** of {rupees(gst_turnover)} is taxable. No audit needed. Saves cost of maintaining full books.")
        elif profile == "Business Owner":
            digital = gst_turnover * (digital_pct / 100)
            cash = gst_turnover - digital
            ad = presumptive_44ad(digital, cash)
            report["numbers"]["presumptive"] = ad
            report["sections"].append({
                "title": "Presumptive Taxation — Section 44AD (Business)",
                "content": f"| Channel | Turnover | Deemed Profit Rate | Profit |\n|:--|:--|:--|:--|\n"
                           f"| Digital | {rupees(digital)} | 6% | {rupees(ad['digital_profit'])} |\n"
                           f"| Cash | {rupees(cash)} | 8% | {rupees(ad['cash_profit'])} |\n"
                           f"| **Total** | {rupees(gst_turnover)} | — | **{rupees(ad['total_profit'])}** |"
            })

        # GST registration threshold
        if gst_turnover > 2000000:
            report["risks"].append(f"**GST Registration Mandatory**: Turnover {rupees(gst_turnover)} exceeds ₹20L threshold (Section 22, CGST Act)")
        if gst_turnover > 10000000:
            report["risks"].append(f"**Tax Audit (44AB)**: Turnover {rupees(gst_turnover)} exceeds ₹1Cr. Tax audit under Section 44AB may be required unless 44AD/44ADA conditions are met.")
        if gst_turnover > 5000000:
            report["risks"].append(f"**E-invoicing Mandatory**: Turnover exceeds ₹5Cr — NIC e-invoicing required for all B2B supplies")

    # 4. Compliance risks
    if has_car:
        bc = blocked_credit_17_5("motor vehicle")
        report["risks"].append(f"**Blocked ITC on Motor Vehicle** — {bc['reason']} (Section {bc['section']})")

    if has_food_expenses:
        bc = blocked_credit_17_5("food catering")
        report["risks"].append(f"**Blocked ITC on Food/Catering** — {bc['reason']} (Section {bc['section']})")

    # 5. Advance tax check
    total_tax = min(new["total_tax"], old["total_tax"])
    cg_tax = report["numbers"].get("capital_gains", {}).get("total_capital_gains_tax", 0)
    combined_tax = total_tax + cg_tax
    if combined_tax > 10000:
        report["risks"].append(f"**Advance Tax Liability**: Combined tax liability of {rupees(combined_tax)} exceeds ₹10,000. "
                               f"You must pay advance tax in quarterly installments (Section 208/234B/234C) to avoid penal interest.")

    # 6. HRA advisory (if salaried and paying rent)
    if profile == "Salaried" and hra > 0:
        report["savings"].append(f"HRA exemption of {rupees(hra)} applied under Section 10(13A) — reduces your Old Regime taxable income")

    if profile == "Salaried" and deductions > 0:
        report["savings"].append(f"Chapter VI-A deductions of {rupees(deductions)} applied in Old Regime (80C: ₹1.5L max, 80D: ₹25K–₹1L, 80CCD(1B): ₹50K NPS)")

    return report


# ==================== WORKSPACES ====================

def home_workspace() -> None:
    st.markdown("""
    <div class="hero">
      <div class="finai-overline">Offline-first. Explainable. Your data stays here.</div>
      <h1>Your private CA<br/>workspace.</h1>
      <p>Describe your financial situation. Get multi-statute tax advisory, GST compliance checks, and optimization strategies — all computed locally without any cloud API.</p>
      <div class="trust-strip"><span>● Deterministic calculations</span><span>● SHA-256 audit chain</span><span>● Optional local AI</span><span>● Date-aware GST rates</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Start here</div>', unsafe_allow_html=True)
    a, b = st.columns([2, 1], gap="large")
    with a:
        st.markdown('<div class="premium-card"><div class="eyebrow">Recommended</div><h3>🧑‍💼 Full CA Consultation</h3><p>Tell FinAI about your income, business, investments, and expenses. Get a unified multi-statute advisory report covering income tax, GST, capital gains, compliance risks, and tax-saving strategies — just like sitting with a CA.</p></div>', unsafe_allow_html=True)
        st.button("Start CA Consultation →", key="go_consult", on_click=navigate, args=("💬 CA Copilot",))
    with b:
        st.markdown('<div class="premium-card"><div class="eyebrow">Individual tools</div><h3>🔧 Use a specific tool</h3><p>Jump directly to GST desk, income tax comparison, capital gains calculator, EMI, or reconciliation.</p></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    cols = st.columns(4, gap="medium")
    tools = [
        ("📊 GST Desk", "📊 GST Desk"), ("📋 Income Tax", "📋 Income Tax"),
        ("📈 Capital Gains", "📈 Capital Gains"), ("🏢 Freelancer / MSME", "🏢 Freelancer / MSME"),
    ]
    for col, (label, target) in zip(cols, tools):
        with col:
            st.button(label, key=f"go_{label}", on_click=navigate, args=(target,))
    cols2 = st.columns(4, gap="medium")
    tools2 = [
        ("🏦 EMI Calculator", "🏦 EMI Calculator"), ("🔍 Reconciliation", "🔍 Reconciliation"),
        ("📚 Legal Knowledge", "📚 Legal Knowledge"), ("📜 Audit History", "📜 Audit History"),
    ]
    for col, (label, target) in zip(cols2, tools2):
        with col:
            st.button(label, key=f"go2_{label}", on_click=navigate, args=(target,))


def copilot_workspace() -> None:
    st.markdown('<div class="eyebrow">Your personal CA advisor</div><div class="section-title">CA Consultation</div><div class="section-subtitle">Fill in your financial details below. FinAI will analyze everything together and produce a comprehensive advisory report — just like a CA would.</div>', unsafe_allow_html=True)

    online, _ = model_status()

    # === AI Chat section (if Ollama is available) ===
    if online:
        st.markdown("---")
        st.markdown("#### 💬 Ask your CA anything")
        st.caption("Ollama is running locally. You can ask follow-up questions about your tax situation in natural language.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="ca-chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ca-chat-msg">🧑‍💼 **CA Pro**: {msg["content"]}</div>', unsafe_allow_html=True)

        user_q = st.chat_input("Ask your CA — e.g. 'Should I opt for 44ADA or maintain regular books?'")
        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.spinner("Thinking..."):
                response = ollama_generate(user_q, CA_SYSTEM_PROMPT)
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            else:
                st.session_state.chat_history.append({"role": "assistant", "content": "I couldn't connect to the local model. Please ensure Ollama is running."})
            st.rerun()
        st.markdown("---")

    # === Guided Consultation Form ===
    st.markdown("#### 📋 Your Financial Profile")

    profile = st.selectbox("Who are you?", ["Salaried", "Freelancer / Professional", "Business Owner"], key="profile")

    col1, col2 = st.columns(2)
    with col1:
        gross = st.number_input("Annual gross income / salary / CTC (₹)", min_value=0.0, value=1200000.0, step=50000.0, key="c_gross")
    with col2:
        gst_turnover = st.number_input(
            "Business / professional gross receipts (₹)" if profile != "Salaried" else "Side-business turnover, if any (₹)",
            min_value=0.0, value=0.0, step=100000.0, key="c_turnover"
        )

    if profile != "Salaried":
        digital_pct = st.slider("% of turnover received digitally (UPI/bank)", 0, 100, 80, key="c_digital")
    else:
        digital_pct = 80.0

    st.markdown("#### 💰 Deductions & Exemptions (Old Regime)")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        deductions = st.number_input("80C + 80D + NPS deductions (₹)", min_value=0.0, value=0.0, step=10000.0, key="c_ded")
    with dc2:
        hra_val = st.number_input("HRA exemption amount (₹)", min_value=0.0, value=0.0, step=10000.0, key="c_hra")
    with dc3:
        home_loan = st.number_input("Home loan interest u/s 24(b) (₹)", min_value=0.0, value=0.0, step=10000.0, key="c_home")

    st.markdown("#### 📈 Capital Gains (if any)")
    cg1, cg2, cg3 = st.columns(3)
    with cg1:
        stcg_val = st.number_input("STCG — equity / MF (₹)", min_value=0.0, value=0.0, step=10000.0, key="c_stcg")
    with cg2:
        ltcg_eq_val = st.number_input("LTCG — equity / MF (₹)", min_value=0.0, value=0.0, step=10000.0, key="c_ltcg_eq")
    with cg3:
        ltcg_prop_val = st.number_input("LTCG — property / gold (₹)", min_value=0.0, value=0.0, step=50000.0, key="c_ltcg_prop")

    st.markdown("#### ⚠️ Expense Categories (for ITC compliance)")
    exp1, exp2 = st.columns(2)
    with exp1:
        has_car = st.checkbox("Purchased / leased a motor vehicle this year", key="c_car")
    with exp2:
        has_food = st.checkbox("Significant food / catering / restaurant expenses", key="c_food")

    interstate = st.checkbox("Primarily interstate transactions (IGST)", key="c_inter")

    # === Generate Report ===
    if st.button("🔍 Generate CA Advisory Report", type="primary"):
        report = run_consultation(
            profile, gross, gst_turnover, interstate, deductions, hra_val,
            home_loan, stcg_val, ltcg_eq_val, ltcg_prop_val, has_car, has_food, digital_pct
        )

        st.markdown("---")
        st.markdown('<div class="section-title">📑 CA Advisory Memorandum</div>', unsafe_allow_html=True)
        st.caption(f"Generated for: {profile} | Gross Income: {rupees(gross)} | Dataset: v{DATASET_VERSION}")

        # Tax-saving opportunities
        if report["savings"]:
            st.markdown("#### ✅ Tax-Saving Opportunities & Recommendations")
            for tip in report["savings"]:
                st.markdown(f'<div class="saving-flag"><p>💡 {tip}</p></div>', unsafe_allow_html=True)

        # Compliance risks
        if report["risks"]:
            st.markdown("#### 🚨 Compliance Risks & Warnings")
            for risk in report["risks"]:
                st.markdown(f'<div class="risk-flag"><p>⚠️ {risk}</p></div>', unsafe_allow_html=True)

        # Detailed sections
        for section in report["sections"]:
            st.markdown(f"#### {section['title']}")
            st.markdown(section["content"])
            st.markdown("---")

        # Save
        inputs = {
            "profile": profile, "gross_income": gross, "gst_turnover": gst_turnover,
            "deductions": deductions, "hra": hra_val, "home_loan": home_loan,
            "stcg": stcg_val, "ltcg_equity": ltcg_eq_val, "ltcg_property": ltcg_prop_val,
        }
        record = save("ca_consultation", inputs, report["numbers"])
        st.success(f"✅ Saved as audit record #{record['id']}")
        with st.expander("🔒 Audit Trail"):
            st.code(f"Record ID    : #{record['id']}\nPrevious Hash: {record['previous_hash']}\nBlock Hash   : {record['hash']}", language="text")


# ==================== INDIVIDUAL TOOL WORKSPACES ====================

def gst_workspace() -> None:
    st.markdown('<div class="eyebrow">Business compliance</div><div class="section-title">GST Desk</div><div class="section-subtitle">Draft a transaction in plain English or use the guided form. Verify the GST treatment, then save.</div>', unsafe_allow_html=True)
    text = st.text_area("Describe the transaction", placeholder="Example: I sold 5 office chairs for ₹45,000 to a customer in Mumbai.", height=100)
    if text:
        draft = parse_transaction(text)
        st.session_state.gst_draft = draft
    draft = st.session_state.get("gst_draft")
    if not draft:
        st.info("Start by describing a sale or purchase above.")
        draft = {"raw": "", "amount": None, "transaction_type": "sale", "interstate": False, "candidates": [], "needs_classification": False, "quick_picks": []}

    if draft.get("needs_classification") and draft.get("quick_picks"):
        st.warning(f"Detected amount **{rupees(draft['amount'])}** but need to know what was {'purchased' if draft['transaction_type'] == 'purchase' else 'sold'}.")
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
        amount = st.number_input("Taxable value (before GST)", min_value=0.0, value=float(draft["amount"] or 0.0), step=1000.0)
        kind = st.selectbox("Type", ["sale", "purchase"], index=0 if draft["transaction_type"] == "sale" else 1)
        interstate = st.toggle("Interstate (IGST)", value=draft["interstate"])
    with right:
        candidates = draft["candidates"] or CATALOG
        options = {f"{item['kind']} {item['code']} — {item['name']} ({item['rate']}%)": item["code"] for item in candidates}
        selected = st.selectbox("HSN/SAC", list(options))
        item = by_code(options[selected])
        st.caption(f"Source: {item['source']}")
        itc_msg = "✅ ITC eligible" if item["itc"] else f"🚫 {item.get('blocked_reason', 'ITC may be blocked')}"
        st.write(itc_msg)

    if kind == "purchase" and not item["itc"]:
        st.error(f"🚫 **Blocked Credit**: ITC ineligible under {item.get('blocked_reason', 'Section 17(5)')}")

    if amount <= 0:
        return

    result = gst(amount, item["rate"], interstate)
    result.update({"classification": {k: item[k] for k in ("code", "kind", "name", "source")}, "tax_treatment": "IGST" if interstate else "CGST + SGST", "itc_message": itc_msg})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Taxable", rupees(result["taxable_value"]))
    c2.metric("GST", rupees(result["gst_amount"]))
    c3.metric("Treatment", result["tax_treatment"])
    c4.metric("Invoice Total", rupees(result["invoice_total"]))

    with st.expander("📖 Statutory Basis"):
        st.markdown(f"""
| Field | Value |
|:--|:--|
| HSN/SAC | `{item['code']}` ({item['kind']}) |
| Classification | {item['name']} |
| Source | {item['source']} |
| Rate | {item['rate']}% |
| Effective From | {item.get('effective_from', '2017-07-01')} |
| Dataset | v{DATASET_VERSION} |
| Calculation | {rupees(result['taxable_value'])} × {item['rate']}% = {rupees(result['gst_amount'])} |
| Invoice Total | {rupees(result['taxable_value'])} + {rupees(result['gst_amount'])} = {rupees(result['invoice_total'])} |
        """)
        val = validate_gst(result["taxable_value"], result["gst_amount"], result["cgst"], result["sgst"], result["igst"], result["invoice_total"], interstate)
        for check in val["checks"]:
            st.write(check)

    if st.button("Confirm and save", type="primary"):
        inputs = {"description": draft["raw"], "amount": amount, "transaction_type": kind, "interstate": interstate, "classification": item["code"]}
        record = save("gst_transaction", inputs, result)
        st.success(f"✅ Saved as audit record #{record['id']}")


def tax_workspace() -> None:
    st.markdown('<div class="eyebrow">Individual planning</div><div class="section-title">Income Tax — Old vs New Regime</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        gross = st.number_input("Annual gross income", min_value=0.0, value=1200000.0, step=25000.0)
        deductions = st.number_input("Old-regime deductions (80C/80D/NPS)", min_value=0.0, value=0.0, step=10000.0)
    with right:
        hra = st.number_input("Eligible HRA exemption", min_value=0.0, value=0.0, step=10000.0)
        home = st.number_input("Home-loan interest (Sec 24b)", min_value=0.0, value=0.0, step=10000.0)

    with st.expander("🏠 Calculate HRA Exemption"):
        hc1, hc2 = st.columns(2)
        with hc1:
            basic = st.number_input("Basic salary (annual)", min_value=0.0, value=600000.0, step=25000.0, key="hb")
            hra_rec = st.number_input("Actual HRA received", min_value=0.0, value=240000.0, step=10000.0, key="hr")
        with hc2:
            rent = st.number_input("Annual rent paid", min_value=0.0, value=240000.0, step=10000.0, key="rp")
            metro = st.checkbox("Metro city (50% of basic)", value=True, key="mt")
        h = hra_exemption(basic, hra_rec, rent, metro)
        st.success(f"**Exempt**: {rupees(h['exempt_hra'])} | **Taxable**: {rupees(h['taxable_hra'])}")
        st.caption(f"Min of: Actual ({rupees(h['actual_hra'])}), {'50' if metro else '40'}% basic ({rupees(h['percent_of_basic'])}), Rent−10% ({rupees(h['rent_minus_10pct'])})")

    new = income_tax(gross, "new")
    old = income_tax(gross, "old", deductions, hra, home)
    winner = "New regime" if new["total_tax"] <= old["total_tax"] else "Old regime"
    savings = abs(new["total_tax"] - old["total_tax"])

    tbl = pd.DataFrame([new, old]).set_index("regime")[["deductions_allowed", "taxable_income", "slab_tax", "rebate", "cess", "total_tax"]]
    st.dataframe(tbl.style.format(rupees), use_container_width=True)
    st.success(f"**{winner}** saves **{rupees(savings)}**")

    with st.expander("📖 Statutory Basis"):
        st.markdown(f"""
- **New Regime (Sec 115BAC)**: ₹75K std deduction, slabs 0-4L(0%), 4-8L(5%), 8-12L(10%), 12-16L(15%), 16-20L(20%), 20-24L(25%), >24L(30%). Rebate up to ₹12L.
- **Old Regime**: ₹50K std deduction + Ch VI-A ({rupees(deductions)}) + HRA ({rupees(hra)}) + Sec 24b ({rupees(home)}). Rebate up to ₹5L.
- 4% Health & Education Cess on tax after rebate.
        """)

    if st.button("Save calculation", type="primary"):
        inputs = {"gross_income": gross, "deductions": deductions, "hra": hra, "home_loan_interest": home}
        result = {"new_regime": new, "old_regime": old, "recommendation": winner, "estimated_difference": savings}
        record = save("personal_tax", inputs, result)
        st.success(f"✅ Saved as audit record #{record['id']}")


def capital_gains_workspace() -> None:
    st.markdown('<div class="eyebrow">Investment taxation</div><div class="section-title">Capital Gains (Budget 2024/25)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        stcg_eq = st.number_input("STCG equity (Sec 111A) [20%]", min_value=0.0, value=50000.0, step=10000.0)
    with c2:
        ltcg_eq = st.number_input("LTCG equity (Sec 112A) [12.5%]", min_value=0.0, value=250000.0, step=10000.0)
    with c3:
        ltcg_prop = st.number_input("LTCG property/gold (Sec 112) [12.5%]", min_value=0.0, value=0.0, step=50000.0)

    res = capital_gains(stcg_eq, ltcg_eq, ltcg_prop)
    m1, m2, m3 = st.columns(3)
    m1.metric("STCG Tax", rupees(res["stcg_tax"]))
    m2.metric("LTCG Equity Tax", rupees(res["ltcg_equity_tax"]))
    m3.metric("LTCG Property Tax", rupees(res["ltcg_property_tax"]))
    st.info(f"Sec 112A exemption: −{rupees(res['ltcg_equity_exemption'])}")
    st.success(f"**Total CG tax (incl 4% cess): {rupees(res['total_capital_gains_tax'])}**")

    if st.button("Save", type="primary", key="cg_save"):
        inputs = {"stcg_equity": stcg_eq, "ltcg_equity": ltcg_eq, "ltcg_property": ltcg_prop}
        record = save("capital_gains", inputs, res)
        st.success(f"✅ Saved as audit record #{record['id']}")


def freelancer_workspace() -> None:
    st.markdown('<div class="eyebrow">Small business & freelancers</div><div class="section-title">Presumptive Taxation (44ADA & 44AD)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Section 44ADA — Professionals")
        p_rec = st.number_input("Gross receipts", min_value=0.0, max_value=7500000.0, value=3500000.0, step=50000.0)
        ada = presumptive_44ada(p_rec)
        st.success(f"**Deemed profit (50%)**: {rupees(ada['taxable_profit'])}")
    with c2:
        st.markdown("#### Section 44AD — Business")
        d_to = st.number_input("Digital turnover (6%)", min_value=0.0, value=8000000.0, step=100000.0)
        c_to = st.number_input("Cash turnover (8%)", min_value=0.0, value=1000000.0, step=100000.0)
        ad = presumptive_44ad(d_to, c_to)
        st.success(f"**Deemed profit**: {rupees(ad['total_profit'])}")

    if st.button("Save", type="primary", key="pt_save"):
        inputs = {"professional_receipts": p_rec, "digital_turnover": d_to, "cash_turnover": c_to}
        result = {"section_44ada": ada, "section_44ad": ad}
        record = save("presumptive_tax", inputs, result)
        st.success(f"✅ Saved as audit record #{record['id']}")


def emi_workspace() -> None:
    st.markdown('<div class="eyebrow">Loan planning</div><div class="section-title">EMI Calculator</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        principal = st.number_input("Principal (₹)", min_value=0.0, value=5000000.0, step=100000.0)
    with c2:
        rate = st.number_input("Rate (% p.a.)", min_value=0.0, max_value=30.0, value=8.5, step=0.25)
    with c3:
        tenure = st.number_input("Tenure (months)", min_value=1, max_value=360, value=240, step=12)

    res = emi(principal, rate, tenure)
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly EMI", rupees(res["monthly_emi"]))
    m2.metric("Total Interest", rupees(res["total_interest"]))
    m3.metric("Total Payment", rupees(res["total_payment"]))

    if st.button("Save", type="primary", key="emi_save"):
        record = save("emi_calculation", {"principal": principal, "rate": rate, "tenure": tenure}, res)
        st.success(f"✅ Saved as audit record #{record['id']}")


def reconciliation_workspace() -> None:
    st.markdown('<div class="eyebrow">Input tax credit</div><div class="section-title">GSTR-2B Reconciliation</div>', unsafe_allow_html=True)
    pc, bc = st.columns(2)
    pf = pc.file_uploader("Purchase register CSV", type="csv")
    gf = bc.file_uploader("GSTR-2B CSV", type="csv")
    if pf and gf:
        purchases, two_b = pd.read_csv(pf), pd.read_csv(gf)
        required = {"invoice_no", "tax_amount"}
        if not required.issubset(purchases.columns) or not required.issubset(two_b.columns):
            st.error("Both files need `invoice_no` and `tax_amount` columns.")
            return
        merged = purchases.merge(two_b[["invoice_no", "tax_amount"]], on="invoice_no", how="left", suffixes=("_purchase", "_2b"))
        merged["status"] = merged["tax_amount_2b"].notna().map({True: "Matched", False: "Missing in GSTR-2B"})
        if "category" in merged.columns:
            bl = merged["category"].apply(lambda c: blocked_credit_17_5(str(c)) if pd.notna(c) else {"is_blocked": False})
            merged["itc_blocked"] = bl.apply(lambda x: x["is_blocked"])
            merged["block_reason"] = bl.apply(lambda x: x.get("reason", ""))
        m1, m2 = st.columns(2)
        m1.metric("Matched ITC", rupees(float(merged.loc[merged.status == "Matched", "tax_amount_purchase"].sum())))
        m2.metric("Missing in 2B", int((merged.status == "Missing in GSTR-2B").sum()))
        st.dataframe(merged, use_container_width=True)
        st.download_button("Download CSV", merged.to_csv(index=False), "reconciliation.csv", "text/csv")


def legal_workspace() -> None:
    st.markdown('<div class="eyebrow">Statutory research</div><div class="section-title">Legal Knowledge Base</div>', unsafe_allow_html=True)
    if st.button("Refresh from official sources"):
        with st.spinner("Downloading and indexing..."):
            count, errors = refresh_legal_sources()
        st.success(f"Indexed {count} sources.")
        for e in errors:
            st.warning(e)
    q = st.text_input("Search GST / income-tax material")
    if q:
        matches = search_legal(q)
        if not matches:
            st.info("No results. Refresh sources first while online.")
        for m in matches:
            st.markdown(f"**[{m['title']}]({m['url']})**")
            st.caption(f"{m['fetched_at']} · {m['topic']}")
            st.write(m["snippet"].replace("[[", "**").replace("]]", "**"))


def audit_workspace() -> None:
    st.markdown('<div class="eyebrow">Traceability</div><div class="section-title">Audit History</div>', unsafe_allow_html=True)
    records = history()
    if not records:
        st.info("No records yet.")
        return
    for row in records:
        with st.expander(f"#{row['id']} · {row['kind']} · {row['created_at']}"):
            inp = json.loads(row["input_json"])
            res = json.loads(row["result_json"])
            st.markdown(f"**Type**: {row['kind']}")
            st.markdown("**Inputs:**")
            for k, v in inp.items():
                st.write(f"  {k}: {v}")
            st.markdown("**Results:**")
            if isinstance(res, dict):
                for k, v in res.items():
                    if isinstance(v, dict):
                        st.write(f"  **{k}**:")
                        for k2, v2 in v.items():
                            st.write(f"    {k2}: {v2}")
                    else:
                        st.write(f"  {k}: {v}")
            st.code(f"Hash: {row['audit_hash']}\nPrev: {row['previous_hash']}", language="text")


# ==================== ROUTING ====================

workspace = sidebar()
if workspace == "🏠 Home":
    home_workspace()
elif workspace == "💬 CA Copilot":
    copilot_workspace()
elif workspace == "📊 GST Desk":
    gst_workspace()
elif workspace == "📋 Income Tax":
    tax_workspace()
elif workspace == "📈 Capital Gains":
    capital_gains_workspace()
elif workspace == "🏢 Freelancer / MSME":
    freelancer_workspace()
elif workspace == "🏦 EMI Calculator":
    emi_workspace()
elif workspace == "🔍 Reconciliation":
    reconciliation_workspace()
elif workspace == "📚 Legal Knowledge":
    legal_workspace()
else:
    audit_workspace()
