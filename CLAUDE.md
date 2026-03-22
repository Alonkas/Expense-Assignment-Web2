# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Roommate Expense Manager — a Streamlit web app for splitting and tracking shared expenses between roommates. Users upload Excel files, assign expenses to partners via a card-based Focus Mode or editable Table View, auto-categorize using learned rules, and export reports to Excel or Google Sheets.

Current version: 4.8.0

## Commands

```bash
# Run the app
streamlit run app.py

# Run setup page in isolation (for testing)
streamlit run setup_page_harness.py

# Run all tests
pytest

# Run a specific test class
pytest tests/test_shared_partner.py::TestCalculateSharedSplit

# Run with coverage
pytest --cov=. tests/

# Install dependencies
pip install -r requirements.txt
```

There is no build step, linter, or type checker configured.

## Architecture

Three-file layered architecture with Streamlit session state as the shared data store:

- **`app.py`** — Main dashboard UI. Renders 6 tabs (Focus Mode, Table View, Final Results, Category Rules, Category Summary, Analytics) plus a sidebar with live partner totals. Entry point.
- **`setup_page.py`** — 4-step setup wizard (upload Excel → confirm column mapping → configure partners → done). Called from `app.py` when `st.session_state.setup_complete` is False.
- **`utils.py`** — All business logic and data I/O. Key functions:
  - `load_excel()` / `auto_detect_columns()` — Excel parsing with Hebrew+English header detection
  - `calculate_shared_split()` — Core shared expense splitting algorithm
  - `generate_excel()` — Multi-sheet Excel report generation (xlsxwriter)
  - `load_categories()` / `save_categories()` / `load_category_rules()` / `save_category_rules()` — Google Sheets persistence
  - `write_to_google_sheets()` — Full export (All Expenses, Summary, per-partner sheets)

Data flows through a single DataFrame in `st.session_state.expenses` with columns: `[Source, Date, Description, Amount, Partner, Category, Comment, Verified]`.

## Key Patterns

- **Category rules engine**: Dict mapping lowercased full descriptions to categories. Exact match only (not substring). Auto-learned during Focus Mode verification and synced to Google Sheets.
- **Shared partner**: Special "Shared" partner with per-partner opt-in (`shares_shared` dict). Shared total is split evenly among opted-in partners.
- **Go-back history**: `verified_history` is a LIFO stack of expense indices. Cleared on Table View saves (index shifting).
- **Google Sheets auth**: Service account via `st.secrets["gcp_service_account"]` + `st.secrets["spreadsheet_id"]` in `.streamlit/secrets.toml`.
- **Private helpers**: Prefixed with underscore (e.g., `_get_spreadsheet()`, `_apply_view()`).

## Testing

Tests are in `tests/test_shared_partner.py`. Key test classes:
- `TestAutoDetectColumns` — Hebrew/English column detection
- `TestCalculateSharedSplit` — Shared expense math
- `TestGenerateExcel` — Excel export
- `TestCategoryRulesMatching` — Auto-categorization
- `TestStreamlitIntegration` — UI flows via Streamlit's AppTest

Google Sheets operations are not tested (require real credentials).

## External Dependencies

- **Google Sheets**: gspread + google-auth (service account). Gracefully degrades if unavailable.
- **Excel**: openpyxl (read), xlsxwriter (write)
- **Charts**: Plotly for pie charts in Analytics tab
