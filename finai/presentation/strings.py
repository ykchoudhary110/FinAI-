"""
FinAI Centralized UI Strings & Localization Scaffolding.
"""

STRINGS = {
    "app_name": "FinAI — Offline Financial AI Assistant",
    "dashboard_title": "FinAI Financial Dashboard",
    "ai_chat_title": "FinAI Offline Co-Pilot",
    "financial_tools_title": "Financial Rule Engine Tools (100% Deterministic)",
    "receipt_scanner_title": "Offline Receipt & Bill OCR Scanner",
    "budget_planner_title": "Budget Planner & What-If Simulator",
    "expense_tracker_title": "Categorized Expense Tracker",
    "investment_planner_title": "Educational Investment Planner",
    "business_advisor_title": "Business Financial Advisor & KPI Insights",
    "reports_title": "Financial PDF Report Generator",
    "search_title": "Global Full-Text Search (SQLite FTS5)",
    "knowledge_base_title": "Offline Finance Documentation",
    "history_title": "History & Calculation Audit Trail",
    "settings_title": "Application Settings & Configuration",
    "about_title": "About FinAI",
    "disclaimer_finance": "⚠️ Educational & Illustrative Projections Only — Not Licensed Investment or Tax Filing Advice.",
    "privacy_banner": "100% Offline Privacy Guaranteed - Zero Telemetry or Outbound Network Calls.",
}


def get_string(key: str, default: str = "") -> str:
    return STRINGS.get(key, default or key)
