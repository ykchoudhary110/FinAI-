# FinAI Offline — Architecture & Safety Rules

```text
User input / guided form
        |
        v
Local deterministic parser ---- optional Ollama local model
        |
        v
Smart clarification (needs_classification → quick-pick chips)
        |
        v
HSN/SAC candidate catalog + explicit user selection
        |
        v
Date-aware GST rate engine (effective_from / effective_to)
        |
        v
Deterministic GST / income-tax / capital-gains / EMI rules
        |
        v
Math validation guardrails (CGST+SGST=GST, base+tax=total)
        |
        v
"Why This Answer?" statutory trace
        |
        v
User confirmation → Save
        |
        v
SQLite record + SHA-256 hash chain + local export
```

## Neuro-Symbolic Principle

- **Neuro layer** (optional): Local LLM via Ollama (Qwen 2.5, Llama 3.2, Phi-3) handles ONLY natural language understanding — intent extraction, entity slot filling, conversational synthesis.
- **Symbolic layer** (mandatory): Deterministic Python rule engines handle ALL calculations, rate lookups, arithmetic, and validation. No LLM ever performs tax math.

## Non-Negotiable Safety Rules

1. A model never performs money calculations.
2. A model never silently decides a low-confidence classification.
3. The user must confirm the classification and place-of-supply facts before saving a GST transaction.
4. A tax calculation only uses entered inputs; it never invents deductions.
5. Every saved result stores inputs, output, preceding audit hash, timestamp, and current audit hash in the local SQLite database.
6. Outputs are drafts, not filing-ready government submissions, until each official schema and statutory data set has been independently validated.
7. Every GST rate returned must be traceable to a stored statutory rate record with notification citation, effective dates, and dataset version.
8. When a product/service is unspecified, the system asks for clarification with quick-pick options — it never guesses a default rate.

## Date-Aware Rate Engine

The GST rate engine (`finai/gst_engine.py`) resolves rates by:
1. Looking up the HSN/SAC code in the versioned master catalog
2. Checking `effective_from` / `effective_to` against the transaction date
3. Computing CGST/SGST (50/50 split) or IGST based on place of supply
4. Flagging ITC eligibility, RCM applicability, cess rates, and Section 17(5) blocked credit
5. Returning the source notification citation for every rate determination

## Dataset Version

Current: `2026.08` — includes 23 HSN/SAC master records covering major tariff chapters and SAC headings with CBIC notification references.
