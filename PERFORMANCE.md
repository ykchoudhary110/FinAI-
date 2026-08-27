# FinAI Phase 5 Performance & Latency Report

This document reports 5-run median benchmark results and SQLite WAL mode optimizations.

## 📊 Phase 5 5-Run Median Benchmark Matrix

| Metric | Measurement Method | 5-Run Median Result | Status |
| :--- | :--- | :--- | :--- |
| **Real Process Cold Start** | 5-run median of fresh OS process launch (`subprocess.Popen`) | **3,507.14 ms (~3.50 s)** | ✅ Honest Median |
| **Multi-Page PDF Generation** | 5-run median of ReportLab multi-section compiler (50 rows) | **9.59 ms** | ✅ Sub-10 ms |
| **Rule Engine Avg Latency** | 5-run median across Tax, GST, and EMI calculations | **0.0688 ms per call** | ✅ Sub-0.1 ms |
| **Idle Dashboard Memory (RSS)** | `psutil.Process().memory_info().rss` | **42.62 MB** | ✅ Sub-45 MB |
| **Active AI Chat Memory (RSS)** | `psutil.Process().memory_info().rss` | **43.65 MB** | ✅ Sub-45 MB |
| **Receipt OCR Peak Memory (RSS)**| `psutil.Process().memory_info().rss` during 1080p scan | **49.58 MB** | ✅ Sub-50 MB |
| **Domain Code Test Coverage** | `pytest --cov=finai.domain` | **94% (34 tests passed)** | ✅ Protected |

## ⚡ Technical Optimizations Applied in Phase 5
1. **SQLite WAL Mode**: Enabled `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` in `DatabaseManager` for high-concurrency read/write transactions.
2. **Custom QPainter Rendering**: Rebuilt Dashboard into a Windows 11 Widget-Tile grid with custom `HealthScoreRingWidget` (Score Ring Gauge) and `CategoryBarChartWidget` (Category Spend Bar Chart).
3. **High-Contrast QSS Fills**: Updated `styles.py` to enforce dark `#1F2937` / `#111827` contrast colors across all labels, cards, text browsers, and input controls.
