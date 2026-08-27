-- Initial Schema for FinAI (0001_init.sql)

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    vendor TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    gst_amount REAL DEFAULT 0.0,
    is_business INTEGER DEFAULT 0,
    notes TEXT,
    receipt_image_path TEXT,
    confidence_score REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT UNIQUE NOT NULL,
    monthly_limit REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gst_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER,
    vendor_gstin TEXT,
    invoice_number TEXT,
    invoice_date TEXT,
    taxable_value REAL NOT NULL,
    cgst REAL DEFAULT 0.0,
    sgst REAL DEFAULT 0.0,
    igst REAL DEFAULT 0.0,
    total_gst REAL NOT NULL,
    itc_claimed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(expense_id) REFERENCES expenses(id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    sender TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    figure_context TEXT, -- Optional JSON string for "Explain this number"
    is_pinned INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nudges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    due_date TEXT,
    is_dismissed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_score_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    score INTEGER NOT NULL,
    savings_score REAL NOT NULL,
    budget_score REAL NOT NULL,
    punctuality_score REAL NOT NULL,
    dti_score REAL NOT NULL,
    gst_score REAL NOT NULL,
    lowest_factor TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendor_category_map (
    vendor_keyword TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
