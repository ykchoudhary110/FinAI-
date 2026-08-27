from finai.domain.rag.knowledge_retriever import retrieve_relevant_kb_passage
from finai.domain.rules.audit_trail import CalculationAuditLedger
from finai.domain.rules.forecast_rules import predict_next_month_spend


def test_forecast_rules():
    expenses = [50000.0, 55000.0, 60000.0, 65000.0]
    res = predict_next_month_spend(expenses)
    assert res.predicted_next_month_spend == 70000.0
    assert res.trend_direction == "Increasing"
    assert res.slope > 0

    # Single value test
    single_res = predict_next_month_spend([45000.0])
    assert single_res.predicted_next_month_spend == 45000.0


def test_audit_trail_ledger_verification():
    ledger = CalculationAuditLedger()

    # Log 3 calculations
    ledger.log_calculation("GST_FORWARD", {"amt": 10000}, {"gst": 1800})
    ledger.log_calculation("INCOME_TAX_NEW", {"income": 1200000}, {"tax": 0})
    ledger.log_calculation("EMI_CALC", {"p": 500000, "r": 8.5, "n": 60}, {"emi": 10258.0})

    valid, checked_count, latest_hash = ledger.verify_integrity()
    assert valid is True
    assert checked_count == 4  # Genesis + 3 logs
    assert len(latest_hash) == 64

    # Tamper with an entry to verify detection
    ledger.chain[2].output_data["tax"] = 50000  # Tampered!
    tampered_valid, _, _ = ledger.verify_integrity()
    assert tampered_valid is False


def test_rag_knowledge_retriever():
    content, title = retrieve_relevant_kb_passage("Tell me tax slabs under Section 87A for 2025")
    assert "Section 87A" in content or "Tax" in title
    assert "Income Tax" in title
