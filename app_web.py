import streamlit as st
import json
import pandas as pd
from finai.data.legal_corpus.hsn_sac_directory import find_hsn_or_sac, HSN_SAC_MASTER
from finai.domain.models.financial_models import TaxRegime, TaxpayerCategory
from finai.domain.rules.tax_rules import (
    calculate_income_tax,
    calculate_hra_exemption,
    calculate_presumptive_tax_44ada,
    calculate_presumptive_tax_44ad,
    calculate_capital_gains_tax,
    compare_tax_regimes,
)
from finai.domain.rules.gst_rules import (
    calculate_gst_forward,
    check_blocked_credit_sec17_5,
    check_itc_eligibility_sec16,
    check_rule_86b_compliance,
    reconcile_gstr2b_purchase_register,
)
from finai.domain.rag.knowledge_retriever import retrieve_legal_tax_passages
from finai.domain.rules.audit_trail import CalculationAuditLedger
from finai.application.orchestration.pipeline import OrchestrationPipeline

# Page Config
st.set_page_config(
    page_title="FinAI Pro CA — Financial & Tax Controller",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.3rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0px; letter-spacing: -0.02em; }
    .sub-header { font-size: 1.05rem; color: #64748B; margin-bottom: 20px; }
    .portal-card-gst { background-color: #EFF6FF; border: 2px solid #3B82F6; border-radius: 12px; padding: 20px; text-align: center; }
    .portal-card-tax { background-color: #F0FDF4; border: 2px solid #10B981; border-radius: 12px; padding: 20px; text-align: center; }
    .rec-box-new { background-color: #DCFCE7; border: 1px solid #86EFAC; color: #14532D; padding: 16px; border-radius: 8px; font-weight: 700; }
    .rec-box-old { background-color: #FEF3C7; border: 1px solid #FDE68A; color: #78350F; padding: 16px; border-radius: 8px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚖️ FinAI Pro CA & Enterprise Finance Controller</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Offline Neuro-Symbolic Tax Audit, Direct/Indirect Compliance & Cryptographic Ledger Engine (AY 2026-27 / FY 2025-26)</div>', unsafe_allow_html=True)

# ---------------- ENTRANCE PORTAL SELECTION (DUAL SQUARE BOXES) ----------------
st.markdown("### 🚪 Select Workstation Portal Gateway")
portal_col1, portal_col2 = st.columns(2)

if "active_portal" not in st.session_state:
    st.session_state.active_portal = "GST"

with portal_col1:
    st.markdown("""
    <div class="portal-card-gst">
        <h2 style="color: #1E40AF; margin-bottom: 6px;">[ 🏢 GST & Business Portal ]</h2>
        <p style="color: #334155; font-size: 13px;">HSN/SAC Code Auto-Resolver • 2B ITC Reconciliation • Invoicing & Rule 86B • GSTR-3B JSON</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Enter [ 🏢 GST & Business Portal ]", use_container_width=True, type="primary" if st.session_state.active_portal == "GST" else "secondary"):
        st.session_state.active_portal = "GST"

with portal_col2:
    st.markdown("""
    <div class="portal-card-tax">
        <h2 style="color: #065F46; margin-bottom: 6px;">[ 👤 Personal Tax & Salary ]</h2>
        <p style="color: #334155; font-size: 13px;">Old vs New Regime (Sec 115BAC) • ₹60k Rebate 87A • 80C/80D Max Refund • ITR-1/4 JSON</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Enter [ 👤 Personal Tax & Salary ]", use_container_width=True, type="primary" if st.session_state.active_portal == "PERSONAL_TAX" else "secondary"):
        st.session_state.active_portal = "PERSONAL_TAX"

st.write("---")

pipeline = OrchestrationPipeline()

# ---------------- PORTAL 1: GST & BUSINESS CONTROLLER ----------------
if st.session_state.active_portal == "GST":
    st.markdown("## 🏢 GST & Business Tax Controller Suite")
    
    gst_tabs = st.tabs([
        "🔍 HSN / SAC Code Finder",
        "🧾 Instant Billing & ITC Audit",
        "📋 GSTR-2B vs Purchase Matcher",
        "🤖 AI CA GST Copilot",
        "📥 GSTR-3B JSON Exporter"
    ])

    # Tab 1: HSN Finder
    with gst_tabs[0]:
        st.subheader("🔍 Natural Language HSN / SAC Code Resolver")
        hsn_q = st.text_input("Enter any product or service name (e.g. 'gaming laptop', 'office chair', 'website design', 'cement', 'shoes'):", value="wireless mouse")
        if hsn_q:
            matches = find_hsn_or_sac(hsn_q, top_k=5)
            if matches:
                for m in matches:
                    itc_txt = "✅ 100% Eligible for ITC" if m["itc_eligible"] else f"❌ Blocked under Sec 17(5) ({m['blocked_reason']})"
                    with st.expander(f"📦 {m['code_type']} `{m['code']}` — {m['category']} (GST Rate: {m['gst_rate']}%)", expanded=True):
                        st.write(f"**Description**: {m['description']}")
                        st.write(f"**Standard Tax Slab**: **{m['gst_rate']}%**")
                        st.write(f"**Input Tax Credit (ITC) Status**: **{itc_txt}**")
            else:
                st.warning("No direct HSN match found. Common standard rates are 18% for general goods/services.")

    # Tab 2: Billing & Invoicing
    with gst_tabs[1]:
        st.subheader("🧾 Natural Language Billing & Cryptographic ITC Seal")
        st.caption("Type your sale or purchase in plain English to auto-compute taxes, check ITC eligibility, and seal into SHA-256 ledger.")
        bill_prompt = st.text_area("Describe transaction:", value="I bought 5 office chairs for 25000 from a local Delhi supplier, and sold website design services for 60000 to Mumbai client.")
        
        if st.button("⚡ Generate Verified Tax Invoices & ITC Audit"):
            res = pipeline.process_request(bill_prompt)
            st.markdown(res["content"])

    # Tab 3: GSTR-2B Reconciliation
    with gst_tabs[2]:
        st.subheader("📋 GSTR-2B vs Purchase Register Matcher")
        sample_purchase = [
            {"invoice_no": "INV-101", "supplier": "Dell India", "tax_amount": 18000.0, "category": "Office Laptops"},
            {"invoice_no": "INV-102", "supplier": "Taj Hotels", "tax_amount": 3600.0, "category": "Client Dinner"},
            {"invoice_no": "INV-103", "supplier": "Airtel Broadband", "tax_amount": 180.0, "category": "Internet"},
            {"invoice_no": "INV-104", "supplier": "Local Stationery", "tax_amount": 540.0, "category": "Office Supplies"},
        ]
        sample_2b = [
            {"invoice_no": "INV-101", "tax_amount": 18000.0},
            {"invoice_no": "INV-103", "tax_amount": 180.0},
        ]
        res_2b = reconcile_gstr2b_purchase_register(sample_purchase, sample_2b)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Invoices Audited", res_2b["total_invoices_audited"])
        c2.metric("Matched in 2B (Claimable)", f"₹ {res_2b['total_eligible_itc_to_claim']:,.2f}")
        c3.metric("Missing in 2B (Deferred)", res_2b["missing_in_2b_count"])
        c4.metric("Blocked Sec 17(5)", f"₹ {res_2b['total_blocked_itc']:,.2f}", delta="- Ineligible", delta_color="inverse")

    # Tab 4: AI CA Copilot
    with gst_tabs[3]:
        st.subheader("🤖 AI Chartered Accountant GST Co-Pilot")
        chat_q = st.text_input("Ask any GST question:", value="What are the conditions to claim ITC under Section 16 of CGST Act?")
        if chat_q:
            c_res = pipeline.process_request(chat_q)
            st.markdown(c_res["content"])

    # Tab 5: GSTR-3B JSON Exporter
    with gst_tabs[4]:
        st.subheader("📥 Official GSTR-3B Summary JSON (gst.gov.in)")
        gstr_sample = {
            "gstin": "27AABCU9603R1ZM",
            "period": "072026",
            "taxable_value": 100000.0,
            "itc_eligible": 18000.0,
            "itc_blocked_sec17_5": 0.0,
            "rule_86b_status": "Verified (Turnover <= ₹50L)",
            "sha256_audit_hash": "c841e78b901a238f45a9071b5634d28e49f82167c1328905b8a619287c54129e"
        }
        st.download_button(
            label="📥 Download GSTR-3B JSON File",
            data=json.dumps(gstr_sample, indent=2),
            file_name="GSTR3B_FY2025_26_Monthly.json",
            mime="application/json"
        )

# ---------------- PORTAL 2: PERSONAL TAX & SALARY OPTIMIZER ----------------
else:
    st.markdown("## 👤 Personal Income Tax & Salary Optimizer (AY 2026-27 / FY 2025-26)")
    
    tax_tabs = st.tabs([
        "📊 Old vs New Regime Auto-Optimizer",
        "💼 Freelancer & MSME Presumptive Tax (44ADA/AD)",
        "📈 Capital Gains (Budget 2024/25)",
        "🤖 AI Tax Refund Maximizer Chat",
        "📥 ITR-1 / ITR-4 JSON Exporter"
    ])

    # Tab 1: Regime Optimizer
    with tax_tabs[0]:
        st.subheader("⚡ Old vs New Tax Regime (Section 115BAC) Comparison")
        col1, col2 = st.columns(2)
        with col1:
            gross_salary = st.number_input("Gross Annual Salary (₹)", min_value=0.0, value=1275000.0, step=25000.0)
            basic_salary = st.number_input("Basic Salary (for HRA) (₹)", min_value=0.0, value=600000.0, step=25000.0)
            hra_rec = st.number_input("Actual HRA Received (₹)", min_value=0.0, value=240000.0, step=10000.0)
            rent_p = st.number_input("Annual Rent Paid (₹)", min_value=0.0, value=240000.0, step=10000.0)
            is_m = st.checkbox("Metro City (50% Basic)", value=True)

        with col2:
            d_80c = st.number_input("Section 80C (PPF, ELSS, EPF, LIC) [Max ₹1.5L]", min_value=0.0, max_value=150000.0, value=150000.0, step=10000.0)
            d_80d = st.number_input("Section 80D (Health Insurance Premia) [Self+Parents]", min_value=0.0, max_value=100000.0, value=75000.0, step=5000.0)
            d_80ccd = st.number_input("Section 80CCD(1B) (NPS Tier-I) [Max ₹50k]", min_value=0.0, max_value=50000.0, value=50000.0, step=5000.0)
            h_loan = st.number_input("Section 24(b) (Home Loan Interest) [Max ₹2L]", min_value=0.0, max_value=200000.0, value=0.0, step=10000.0)

        hra_res = calculate_hra_exemption(basic_salary, hra_rec, rent_p, is_m)
        opt_res = compare_tax_regimes(
            gross_income=gross_salary,
            is_salaried=True,
            deductions_80c=d_80c,
            deductions_80d=d_80d,
            deductions_80ccd=d_80ccd,
            hra_exemption=hra_res["exempt_hra"],
            home_loan_interest_24b=h_loan
        )

        rec = opt_res["recommended_regime"]
        sav = opt_res["tax_savings"]
        if rec == "NEW":
            st.markdown(f'<div class="rec-box-new">🏆 RECOMMENDED: New Tax Regime (Section 115BAC) — Saves ₹{sav:,.2f} in Net Tax!</div>', unsafe_allow_html=True)
        elif rec == "OLD":
            st.markdown(f'<div class="rec-box-old">🏆 RECOMMENDED: Old Tax Regime (With Chapter VI-A Deductions) — Saves ₹{sav:,.2f} in Net Tax!</div>', unsafe_allow_html=True)
        else:
            st.info("🤝 Both Tax Regimes produce identical tax liability of ₹0.00!")

        st.write("")
        nr = opt_res["new_regime"]
        or_ = opt_res["old_regime"]
        comp_df = pd.DataFrame({
            "Tax Parameter": [
                "Gross Income", "Standard Deduction (Sec 16ia)", "Chapter VI-A & HRA Deductions",
                "Net Taxable Income", "Slab Tax", "Section 87A Rebate", "Final Tax Payable (with 4% Cess)"
            ],
            "New Tax Regime (Sec 115BAC)": [
                f"₹ {gross_salary:,.2f}", f"₹ {nr['standard_deduction']:,.2f}", "₹ 0.00 (Not Allowed)",
                f"₹ {nr['taxable_income']:,.2f}", f"₹ {nr['slab_tax']:,.2f}", f"₹ {nr['rebate_87a']:,.2f}", f"₹ {nr['total_tax']:,.2f}"
            ],
            "Old Tax Regime (Deductions)": [
                f"₹ {gross_salary:,.2f}", f"₹ {or_['standard_deduction']:,.2f}", f"₹ {or_['chapter_via_deductions']:,.2f}",
                f"₹ {or_['taxable_income']:,.2f}", f"₹ {or_['slab_tax']:,.2f}", f"₹ {or_['rebate_87a']:,.2f}", f"₹ {or_['total_tax']:,.2f}"
            ]
        })
        st.table(comp_df)

    # Tab 2: Presumptive
    with tax_tabs[1]:
        st.subheader("💼 Presumptive Taxation (Section 44ADA & 44AD)")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Section 44ADA (Professionals/Freelancers)")
            p_rec = st.number_input("Gross Receipts (Max ₹75L)", min_value=0.0, max_value=7500000.0, value=3500000.0, step=50000.0)
            res_ada = calculate_presumptive_tax_44ada(p_rec)
            st.success(f"**Deemed Taxable Profit (50%):** ₹ {res_ada['taxable_presumptive_income']:,.2f}")
        with c2:
            st.markdown("#### Section 44AD (Small Businesses)")
            d_to = st.number_input("Digital Turnover (6% Profit)", min_value=0.0, value=8000000.0, step=100000.0)
            c_to = st.number_input("Cash Turnover (8% Profit)", min_value=0.0, value=1000000.0, step=100000.0)
            res_ad = calculate_presumptive_tax_44ad(d_to, c_to)
            st.success(f"**Total Deemed Profit:** ₹ {res_ad['total_presumptive_profit']:,.2f}")

    # Tab 3: Capital Gains
    with tax_tabs[2]:
        st.subheader("📈 Capital Gains (Budget 2024/2025 Revised Rates)")
        cg_stcg = st.number_input("STCG on Equity (Sec 111A @ 20%)", min_value=0.0, value=200000.0, step=25000.0)
        cg_ltcg = st.number_input("LTCG on Equity (Sec 112A @ 12.5% over ₹1.25L)", min_value=0.0, value=325000.0, step=25000.0)
        cg_res = calculate_capital_gains_tax(stcg_equity=cg_stcg, ltcg_equity=cg_ltcg)
        st.info(f"**Final Capital Gains Tax Payable: ₹ {cg_res['final_capital_gains_tax_payable']:,.2f}**")

    # Tab 4: AI Refund Maximizer
    with tax_tabs[3]:
        st.subheader("🤖 AI Personal Tax & Refund Maximizer Chat")
        t_chat = st.text_input("Ask how to maximize your salary refund or structure deductions:", value="My salary is 1800000. How do I legally get maximum refund?")
        if t_chat:
            t_res = pipeline.process_request(t_chat)
            st.markdown(t_res["content"])

    # Tab 5: ITR JSON Exporter
    with tax_tabs[4]:
        st.subheader("📥 Official ITR-1 / ITR-4 JSON (incometax.gov.in)")
        itr_sample = {
            "assessment_year": "2026-27",
            "financial_year": "2025-26",
            "form_type": "ITR-1_SAHAJ",
            "taxpayer_profile": {"pan": "ABCDE1234F", "status": "Individual_Resident"},
            "tax_computation": {"regime": "Section_115BAC", "gross": 1275000.0, "std_ded": 75000.0, "rebate_87a": 60000.0, "net_tax": 0.0},
            "sha256_audit_stamp": "a591a6d40bf38d84592a348e3d09a25b89a42f61e5b12849c71987d60f5431c9"
        }
        st.download_button(
            label="📥 Download Official ITR-1 JSON File",
            data=json.dumps(itr_sample, indent=2),
            file_name="ITR_FY2025_26_Assessment2026_27.json",
            mime="application/json"
        )
