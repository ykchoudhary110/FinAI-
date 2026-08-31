# FinAI — Offline-First Indian Finance & Tax Intelligence

> **Authors**: Yash Kumar Choudhary¹, Vaibhav Saini¹, Utkarsh Kumar¹, Dr. Shelja Sharma²

An offline-first, neuro-symbolic Indian finance and tax application. FinAI uses deterministic Python rule engines for all money calculations and optionally uses a local open-source Ollama model only to understand free-form natural language.

## Features

### GST & Business Desk
- **Natural language transaction drafting** — describe a sale/purchase in plain English
- **Smart clarification** — when product/service is unspecified, quick-pick chips appear instead of guessing a rate
- **22+ HSN/SAC master catalog** — versioned records with effective dates, CBIC notification citations, ITC eligibility, RCM flags, and cess rates
- **Date-aware GST rate engine** — validates rates against `effective_from` / `effective_to` windows
- **Math validation guardrails** — verifies CGST+SGST=GST, Base+Tax=Total, non-negative constraints
- **Section 17(5) blocked credit detection** — flags motor vehicles, food/catering, travel, insurance, gifts
- **"Why This Answer?"** — every result shows the statutory notification, classification basis, formula, and validation checks

### Personal Tax Desk
- **Old vs New regime comparison** — Budget 2024/25 slabs with correct rebate under Section 87A
- **HRA exemption calculator** — minimum of 3 rules (actual HRA, % of basic, rent minus 10%)
- **Regime recommendation** with savings amount

### Capital Gains (Budget 2024/25)
- STCG equity at **20%** (Section 111A)
- LTCG equity at **12.5%** (Section 112A) with **₹1,25,000 exemption**
- LTCG property/gold at **12.5%** (no indexation post Budget 2024)
- 4% Health & Education Cess

### Freelancer & MSME
- **Section 44ADA** — 50% deemed profit for professionals (up to ₹75L)
- **Section 44AD** — 6% digital + 8% cash turnover for small businesses (up to ₹3Cr)

### EMI Calculator
- Standard reducing-balance EMI formula
- Total interest and total payment breakdown

### GSTR-2B Reconciliation
- Upload purchase register CSV and GSTR-2B CSV
- Automatic matching with Matched / Missing status
- Section 17(5) blocked credit flagging on reconciled invoices

### Legal Knowledge Base
- Downloads and indexes 5 official government sources (CBIC, Income Tax Dept, GST Portal)
- SQLite FTS5 full-text search works offline after initial refresh

### Audit History
- Every saved record contains inputs, calculation output, and SHA-256 hash chain reference
- Tamper-evident: each record's hash depends on the previous record's hash

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full safety rules and neuro-symbolic design.

```
finai/
├── catalog.py         # 23 HSN/SAC records, versioned, with notifications
├── gst_engine.py      # Date-aware rate resolution
├── validators.py      # Math validation guardrails
├── rules.py           # GST, income tax, capital gains, EMI, HRA, 44ADA, 44AD, 17(5), 86B
├── parser.py          # NLP parser with smart clarification
├── storage.py         # SQLite audit ledger with SHA-256 chain
├── local_model.py     # Ollama status checker
├── legal_sources.py   # FTS5 legal knowledge base
app.py                 # Streamlit web UI (8 workspaces)
tests/test_all.py      # 45+ automated tests
```

## Run Locally

Install Python 3.12+, then:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Or double-click `start_finai.bat`.

## Optional Local AI Model

Install [Ollama](https://ollama.ai), then download one model while online:

```powershell
ollama pull qwen2.5:3b
ollama serve
```

The app never sends data to a cloud service. If Ollama is unavailable, FinAI uses its deterministic parser and guided forms.

## Run Tests

```powershell
python -m pytest tests/ -v
```

## Important

This project is an educational/demo tool, not filing software or professional tax advice. Validate current rules, notifications, and official schemas before filing.
