# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Roommate Expense Manager — a Streamlit web app for splitting and tracking shared expenses between roommates. Users upload Excel files, assign expenses to partners via a card-based Focus Mode or editable Table View, auto-categorize using learned rules, and export reports to Excel.

Current version: 5.1.0

## Commands

```bash
# Run the app
streamlit run app.py

# Run setup page in isolation (for testing)
streamlit run setup_page_harness.py

# Install dependencies
pip install -r requirements.txt
```

There is no build step, linter, type checker, or test suite configured. Tests existed previously (`tests/test_shared_partner.py`) but were removed.

## Architecture

Three-file layered architecture with Streamlit session state as the shared data store:

- **`app.py`** — Main dashboard UI. Renders 6 tabs (Focus Mode, Table View, Final Results, Settings, Category Summary, Analytics) plus a sidebar with live partner totals. Entry point.
- **`setup_page.py`** — 4-step setup wizard (upload Excel → confirm column mapping → configure partners → done). Called from `app.py` when `st.session_state.setup_complete` is False.
- **`utils.py`** — All business logic and data I/O. Key functions:
  - `auto_detect_columns()` / `apply_mapping()` — Excel parsing with Hebrew+English header detection
  - `calculate_shared_split()` — Core shared expense splitting algorithm
  - `generate_excel()` — Multi-sheet Excel report generation (xlsxwriter)
  - `load_categories()` / `save_categories()` / `load_category_rules()` / `save_category_rules()` — Local CSV persistence in `data/`

Data flows through a single DataFrame in `st.session_state.expenses` with columns: `[Source, Date, Description, Amount, Partner, Category, Comment, Verified]`.

## Key Patterns

- **Category rules engine**: Dict mapping lowercased full descriptions to categories. Exact match only (not substring). Auto-learned during Focus Mode verification. Stored locally in `data/category_rules.csv`.
- **Local CSV persistence**: Category rules and categories are stored as CSV files in `data/`. The Settings tab lets users open `data/category_rules.csv` in Excel and reload rules from file.
- **Shared partner**: Special "Shared" partner with per-partner opt-in (`shares_shared` dict). Shared total is split evenly among opted-in partners.
- **Go-back history**: `verified_history` is a LIFO stack of expense indices. Cleared on Table View saves (index shifting).
- **Private helpers**: Prefixed with underscore (e.g., `_apply_view()`).
- **Dark theme**: Hardcoded dark theme via `.streamlit/config.toml` (`base = "dark"`) plus custom CSS in `app.py`.

## External Dependencies

- **Excel**: openpyxl (read), xlsxwriter (write)
- **Charts**: Plotly for pie charts in Analytics tab
