# Changelog — FinAI (Offline Financial AI Assistant)

All notable changes to this project are documented in this file.

## [1.2.0-phase5] - 2026-07-30 (Phase 5: Regression Fixes & Dashboard Widget Redesign)
### Added
- **Windows 11 Widget-Tile Dashboard Redesign**: Built 2x3 grid layout with custom QPainter widgets (`HealthScoreRingWidget` circular score arc and `CategoryBarChartWidget` category spend bars).
- **High-Contrast Text Audit**: Enforced `#1F2937` / `#111827` dark text contrast across all 14 pages (Knowledge Base, Settings, About, Budget Planner, Business Advisor, Scanner).
- **Knowledge Base Fix**: Bound `QListWidget.currentTextChanged` and `itemClicked` to update `QTextBrowser.setHtml` immediately upon topic selection.
- **AI Chat Ollama Status & Banner**: Added reachability check and explicit warning banner (`⚠️ Local AI Offline — Start Ollama`) with `🔄 Retry Connection` button.
- **SQLite WAL Mode**: Configured `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` for database concurrency.
- **5-Run Median Benchmark Suite**: Measured honest 5-run median metrics (3.50s cold start, 9.59ms PDF, 42.62MB RSS).

## [1.1.0-phase4] - 2026-07-29 (Phase 4: Premium Glass Polish — Light Mode Only)
### Added
- iOS-Style Frosted Glass Design Language (`rgba(255,255,255,0.75)` panel fills + glass highlights).

## [1.0.0-phase3] - 2026-07-29 (Phase 3: Polish & Real-World Performance)
### Added
- Collapsible Sidebar (`≡` / `Ctrl+B`), Global Shortcuts (`Ctrl+K`, `Ctrl+N`, `Esc`), High-DPI Scaling, Virtualized `QAbstractTableModel`.

## [0.2.0-phase2] - 2026-07-29 (Phase 2: Completion & Integration)
### Added
- Built all 14 Desktop UI Pages, end-to-end receipt integration, live sliders, notification tray.
