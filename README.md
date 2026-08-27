# ⚖️ FinAI — On-Device Neuro-Symbolic Tax Audit & Enterprise Financial Controller

> **A 100% Offline, Privacy-Preserving AI Chartered Accountant & Financial Compliance Workstation**
> Built for Salaried Employees, Freelancers (Sec 44ADA), MSMEs (Sec 44AD), and B2B Taxpayers in India.

---

## 👥 **Authors & Research Team**
- **Yash Kumar Choudhary¹**, **Vaibhav Saini¹**, **Utkarsh Kumar¹**, **Dr. Shelja Sharma²**
- *Department of Computer Science & Engineering, Faculty of Engineering & Technology*
- `{yash.choudhary, vaibhav.saini, utkarsh.kumar, shelja.sharma}@university.edu.in`

---

## 🌟 **Key Innovations & Capabilities**

1. **🚪 Dual Compliance Portal Gateway**:
   - **`[ 🏢 GST & Business Portal ]`**: Natural language HSN/SAC resolution, GSTR-2B automated ITC reconciliation, Section 17(5) blocked credit protection, Rule 86B 1% cash check, and official GSTR-3B JSON exports.
   - **`[ 👤 Personal Tax & Salary Optimizer ]`**: Old vs New Regime (Section 115BAC) auto-optimizer, ₹60k Section 87A rebate, Section 10(13A) HRA least-of-three calculation, Budget 2024/25 Capital Gains tax, and official ITR-1/4 JSON exports.

2. **🧠 Neuro-Symbolic AI Architecture (Zero Hallucinations)**:
   - Eliminates LLM arithmetic errors by strictly delegating mathematical calculations to **deterministic Python domain rule engines**.
   - Language models (**Meta Llama 3.2 3B / Microsoft Phi-3 Mini**) are utilized purely for conversational synthesis and legal guidance.

3. **📚 Sub-Millisecond Offline Legal RAG (54+ Statutory Chunks)**:
   - Grounded in primary Indian statutory law: *Income Tax Act 1961*, *CGST Act 2017*, *Central Board Circulars*, *PwC Worldwide Tax Summaries*, and landmark *Supreme Court Precedents* (*Safari Retreats*, *Bharti Airtel*).
   - Average retrieval latency: **0.23 ms** via SQLite FTS5.

4. **🔍 Natural Language HSN / SAC Code Resolver**:
   - Matches plain English queries (e.g., *"wireless mouse"*, *"software consulting"*, *"office chairs"*) to official 4/6/8-digit HSN/SAC codes, tax rates, and ITC eligibility.

5. **🧾 Conversational Billing & Invoicing**:
   - Type transactions naturally (e.g., *"I bought 5 desks for ₹25,000 and sold software for ₹60,000"*).
   - Automatically computes CGST/SGST/IGST, audits ITC under Section 16 & 17(5), and seals the transaction in an **append-only SHA-256 cryptographic ledger** (mini-blockchain).

6. **📥 1-Click Government E-Filing Exporters**:
   - **ITR-1 / ITR-4 JSON**: Directly uploadable to `incometax.gov.in`.
   - **GSTR-3B Summary JSON**: Directly uploadable to `gst.gov.in`.
   - **Branded CA Statement of Total Income (PDF)**: High-resolution printable PDF with ReportLab formatting, CA seal, and SHA-256 verification hash.

---

## 🗺️ **System Architecture**

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                      1. PRESENTATION / CLIENT LAYER                       │
│   • PySide6 Desktop Workstation (.exe)   • Streamlit Web Demo (app_web.py)│
│   • Dual Portal Gateway: [🏢 GST & Business] vs [👤 Personal Tax & Salary]│
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                 2. APPLICATION ORCHESTRATION PIPELINE                     │
│  [Natural Query / Invoice OCR] ──► [Intent Detector & Slot Planner]       │
└──────────────────┬──────────────────────────────────────┬─────────────────┘
                   │ (Extracts Legal Intent)              │ (Extracts Numbers & Params)
                   ▼                                      ▼
┌──────────────────────────────────────┐  ┌─────────────────────────────────┐
│       3. "NEURO" LAYER (RAG)         │  │    4. "SYMBOLIC" LAYER (CODE)   │
│ • Local LLM (Llama 3.2 / Phi-3)      │  │ • Tax Engine (Sec 115BAC / 87A) │
│ • SQLite FTS5 Statutory Search       │  │ • GST 2B & Sec 17(5) Blocked ITC│
│ • 54+ Statutory Corpus Chunks        │  │ • Budget 2024/25 Capital Gains  │
│ • HSN / SAC Auto-Resolver            │  │ • 100% Deterministic Python Math│
└──────────────────┬───────────────────┘  └───────────────┬─────────────────┘
                   │                                      │
                   └──────────────────┬───────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│            5. VALIDATOR, CRYPTOGRAPHIC LEDGER & EXPORT LAYER              │
│   • Output Guardrail & Domain Sanity Validator                            │
│   • Append-Only SHA-256 Cryptographic Hash Chain (Tamper-Proof Audit)     │
│   • Official Government Schema Exporters (ITR-1/4 JSON & GSTR-3B JSON)    │
│   • High-Resolution Branded CA PDF Computation Statements                 │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 **Quick Start & Installation**

### 1. Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/) (Optional for on-device LLM conversation):
  ```bash
  ollama pull llama3.2:3b
  ```

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/ykchoudhary110/FinAI-.git
cd FinAI-
pip install -r requirements.txt
```

### 3. Run the Desktop Application (PySide6)
```bash
python -m finai.presentation.app_shell
```
*Or double-click `Launch_FinAI_Pro_CA.bat` on Windows.*

### 4. Run the Web App (Streamlit)
```bash
streamlit run app_web.py
```

### 5. Run the Automated Test Suite (42/42 Tests)
```bash
python -m pytest
```

---

## 🛡️ **Empirical Benchmark & Evaluation Results**

- **Total Test Benchmark Cases**: 42 / 42 (100% Passing)
- **Top-1 Statutory Retrieval Precision**: 100.0%
- **Statutory Citation Accuracy**: 100.0%
- **Neuro-Symbolic Rule Verification**: 100.0%
- **Mean Offline Retrieval Latency**: 0.23 ms (SQLite FTS5)

---

## 📄 **License**
This project is licensed under the MIT License — see the LICENSE file for details.
