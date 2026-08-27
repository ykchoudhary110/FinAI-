# FinAI — Architecture & System Design Document

FinAI is a 100% offline, Windows 11-styled desktop financial co-pilot for individuals, freelancers, and small businesses in India.

## 1. Four-Tier Architecture

FinAI strictly enforces Dependency Inversion across four distinct architectural tiers:

```
+-------------------------------------------------------------+
| Tier 1: Presentation (PySide6 Widget-Tile & Glass UI)       |
|   - Windows 11 Widget Grid Dashboard + QPainter Score Ring  |
|   - QPainter Category Spend Bar Chart                       |
|   - 14 Full Pages with High-Contrast Dark Text (#1F2937)    |
|   - High-DPI Scaling Enabled (100%, 125%, 150%)             |
|   - Virtualized QAbstractTableModel for Sub-ms Rendering    |
|   - Global Shortcuts & Crash Safety Hook                    |
+-------------------------------------------------------------+
                              | (View-Model / Service interfaces)
                              v
+-------------------------------------------------------------+
| Tier 2: Application (Orchestration & Use Cases)             |
|   - Two-Stage Intent Classifier (Regex -> Ollama JSON)      |
|   - Planner, Validator & Master Pipeline Coordinator        |
|   - SaveScannedReceiptUseCase (End-to-End Module Sync)       |
|   - APScheduler Background Nudge Engine                     |
+-------------------------------------------------------------+
                              | (Repository / Domain interfaces)
                              v
+-------------------------------------------------------------+
| Tier 3: Domain (Deterministic Rule Engine & OCR Parser)     |
|   - Pure Math Rules (GST, Income Tax FY25-26, EMI, Health)  |
|   - OCR Text Parser & Pydantic Value Objects (94% Cover)    |
+-------------------------------------------------------------+
                              | (Data contracts)
                              v
+-------------------------------------------------------------+
| Tier 4: Data (SQLite WAL Mode, FTS5 Search, Encrypted Backup)|
|   - PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;     |
|   - Versioned Migrations (0001_init.sql, 0002_add_fts5.sql)  |
|   - SQLite FTS5 Full-Text Search Repository                 |
|   - Fernet AES + PBKDF2 Encrypted Backup & Restore          |
|   - ReportLab PDF Report Generator                          |
+-------------------------------------------------------------+
```

## 2. Real-World Performance & Memory Metrics (Phase 5 5-Run Median)
- **Real Process Cold-Start (5-Run Median)**: 3.50 s.
- **Rule Engine Latency (5-Run Median)**: 0.0688 ms per calculation.
- **Idle Memory Footprint (RSS)**: 42.62 MB.
- **Receipt OCR Peak Memory (RSS)**: 49.58 MB.
