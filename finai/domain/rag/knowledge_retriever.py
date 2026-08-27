from dataclasses import dataclass
from typing import List, Tuple
from finai.data.legal_corpus.legal_corpus_seed import SEED_LEGAL_CORPUS, LegalDocumentChunk


@dataclass
class KBArticleSnippet:
    title: str
    content: str
    category: str


LOCAL_KB_DOCUMENTS: List[KBArticleSnippet] = [
    KBArticleSnippet(
        title="Income Tax Slabs & Deductions Guide (FY 2025-26)",
        content="Under the New Tax Regime for FY 2025-26, standard deduction for salaried individuals is ₹75,000. Under Section 87A, full tax rebate is available for taxable income up to ₹12.00 Lakhs, resulting in zero net tax liability. Tax slabs: 0-4L (0%), 4-8L (5%), 8-12L (10%), 12-16L (15%), 16-20L (20%), 20-24L (25%), Above 24L (30%).",
        category="Income Tax"
    ),
    KBArticleSnippet(
        title="GST Input Tax Credit (ITC) Rules & Rates",
        content="GST standard slabs in India are 5%, 12%, 18%, and 28%. Business entities can claim Input Tax Credit (ITC) on B2B purchases with valid GSTIN tax invoices. CGST and SGST split 50/50 for intrastate transactions, while IGST applies to interstate supply.",
        category="GST"
    ),
    KBArticleSnippet(
        title="Loan EMI & Reducing Balance Interest Calculation",
        content="Equated Monthly Installment (EMI) is calculated using E = P * r * (1+r)^n / ((1+r)^n - 1), where P is principal, r is monthly interest rate, and n is tenure in months. In reducing balance interest, each payment reduces principal, lowering interest in subsequent months.",
        category="EMI"
    ),
    KBArticleSnippet(
        title="Emergency Fund & 50-30-20 Budget Rule",
        content="Financial health guidelines recommend maintaining an emergency liquidity cushion equal to 6 months of essential expenses. The 50/30/20 budget framework allocates 50% income to needs, 30% to wants, and 20% to savings/debt repayment.",
        category="Budgeting"
    ),
]


def retrieve_relevant_kb_passage(query: str) -> Tuple[str, str]:
    """
    Retrieves the most relevant local KB document snippet using TF-IDF / keyword similarity matching.
    Returns: (passage_text, source_title)
    """
    query_words = set(query.lower().split())
    best_score = 0
    best_doc = LOCAL_KB_DOCUMENTS[0]

    for doc in LOCAL_KB_DOCUMENTS:
        doc_words = set((doc.title + " " + doc.content).lower().split())
        overlap = len(query_words.intersection(doc_words))
        if overlap > best_score:
            best_score = overlap
            best_doc = doc

    return best_doc.content, best_doc.title


def retrieve_legal_tax_passages(query: str, top_k: int = 3) -> List[Tuple[LegalDocumentChunk, float]]:
    """
    Retrieves top-k relevant legal document chunks from primary Indian legal corpus
    using keyword overlap scoring with topic tag weighting.
    Returns list of tuples: (chunk, score)
    """
    query_terms = [q.lower().strip() for q in query.split() if len(q.strip()) > 2]
    if not query_terms:
        return [(SEED_LEGAL_CORPUS[0], 1.0)]

    scored_chunks = []
    for chunk in SEED_LEGAL_CORPUS:
        searchable_text = f"{chunk.statute_name} {chunk.section_no} {chunk.title} {chunk.content} {' '.join(chunk.topic_tags)}".lower()
        score = 0.0
        for term in query_terms:
            if term in searchable_text:
                score += 1.0
                # Give bonus weight for section or statute matches
                if term in chunk.section_no.lower() or term in chunk.statute_name.lower():
                    score += 2.0
                if any(term in tag.lower() for tag in chunk.topic_tags):
                    score += 1.5

        if score > 0:
            scored_chunks.append((chunk, score))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    if not scored_chunks:
        return [(SEED_LEGAL_CORPUS[0], 0.5)]

    return scored_chunks[:top_k]
