# Codebase Structure

**Analysis Date:** 2026-03-16

## Directory Layout

```
Expense-Assignment/
├── app.py                      # Main Streamlit entry point (486 lines)
├── setup_page.py               # Setup wizard UI (125 lines)
├── setup_page_harness.py       # Minimal test harness for setup_page
├── utils.py                    # Shared business logic (291 lines)
├── requirements.txt            # Python dependencies
├── run.bat                      # Windows batch runner
├── README.md                    # Project documentation
├── .streamlit/
│   ├── config.toml             # Streamlit theme config
│   └── secrets.toml            # Google Sheets credentials (not committed)
├── .claude/
│   └── settings.local.json     # Claude IDE settings
├── .planning/
│   └── codebase/               # Generated codebase analysis documents
└── tests/
    ├── __init__.py
    └── test_shared_partner.py  # Unit + integration tests (336 lines)
```

## Directory Purposes

**Root Directory (`/`):**
- Purpose: Project entry point and main application files
- Contains: Python modules (app.py, setup_page.py, utils.py), config, docs
- Key files: `app.py` (main), `requirements.txt` (dependencies)

**.streamlit/:**
- Purpose: Streamlit framework configuration
- Contains: Theme settings (config.toml), authentication secrets (secrets.toml)
- Key files: `config.toml` (enforces dark theme base), `secrets.toml` (Google API credentials)

**tests/:**
- Purpose: Unit and integration tests
- Contains: Pytest test suites with fixtures and mocks
- Key files: `test_shared_partner.py` (shared expense logic, Excel export, category rules, go-back history)

**.planning/codebase/:**
- Purpose: Generated documentation from GSD analysis tools
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md
- Key files: Auto-generated; consumed by `/gsd:plan-phase` and `/gsd:execute-phase`

**.claude/:**
- Purpose: Claude IDE and agent settings
- Contains: IDE configuration, tool preferences
- Key files: `settings.local.json` (user-specific IDE settings)

## Key File Locations

**Entry Points:**
- `app.py`: Main Streamlit application; run with `streamlit run app.py`
- `setup_page_harness.py`: Isolated setup page testing; run with `streamlit run setup_page_harness.py`

**Configuration:**
- `.streamlit/config.toml`: Theme base color (dark)
- `.streamlit/secrets.toml`: Google Sheets API credentials (SERVICE_ACCOUNT_JSON, spreadsheet_id) — DO NOT COMMIT
- `requirements.txt`: Python package dependencies

**Core Logic:**
- `app.py`: Dashboard tabs (Focus Mode, Table View, Results, Category Rules, Analytics), session initialization, sidebar totals
- `setup_page.py`: Partner setup, multi-file Excel upload with column mapping, progress display
- `utils.py`: Business functions for data loading, calculations, and persistence

**Testing:**
- `tests/test_shared_partner.py`: Pytest test suite with three test classes
  - `TestCalculateSharedSplit`: Logic for splitting shared expenses (6 tests)
  - `TestGenerateExcel`: Excel export with/without shared partner (4 tests)
  - `TestStreamlitIntegration`: Streamlit.testing.v1 UI tests (2 tests)
  - `TestCategoryRulesMatching`: Description→category exact matching (6 tests)
  - `TestGoBackHistory`: Verified_history stack logic (3 tests)

## Naming Conventions

**Files:**
- `app.py`: Main entry point (lowercase, no underscores)
- `setup_page.py`: Feature module (lowercase with underscores for multi-word)
- `utils.py`: Utility/shared functions module
- `test_*.py`: Test files (pytest convention: test_<module>.py)
- `*_harness.py`: Test harness to isolate a component (mimics setup_page for testing)

**Functions:**
- `render_setup_page()`: Streamlit page renderer (camelCase prefix render_)
- `load_excel()`, `load_categories()`: Data loaders (verb_noun pattern)
- `save_categories()`, `save_category_rules()`: Data savers (verb_noun pattern)
- `extract_categories()`, `calculate_shared_split()`: Transformers (verb_noun pattern)
- `_get_spreadsheet()`: Private helper (leading underscore, lowercase with underscores)
- `_apply_view()`: Private helper in app.py (leading underscore)

**Variables:**
- `st.session_state.expenses`: DataFrame (plural noun)
- `st.session_state.partners`: Dict[str, str] (plural noun)
- `st.session_state.categories`: List[str] (plural noun)
- `st.session_state.category_rules`: Dict[str, str] (lowercase with underscores)
- `has_shared_partner`: Boolean flag (has_<feature> pattern)
- `curr_idx`, `col_idx`: Index variables (abbreviations acceptable in tight loops)
- `df`: DataFrame (standard pandas abbreviation)

**Types:**
- `pd.DataFrame`: Pandas tabular data
- `dict`: Python dictionary for config (partners → colors, rules → categories)
- `list`: Python list for ordered collections (categories)

## Where to Add New Code

**New Feature (e.g., Expense Filtering):**
- Primary code: `utils.py` (add pure function like `filter_expenses_by_date()`)
- UI component: `app.py` (add to appropriate tab or new tab)
- Tests: `tests/test_shared_partner.py` (add new test class or method)

**New Component/Module (e.g., Budget Tracking):**
- Implementation: Create `budget_page.py` (following `setup_page.py` pattern)
- Shared logic: Add helpers to `utils.py`
- Integration: Import and call from `app.py` similar to `render_setup_page()`

**Utilities:**
- Shared helpers: `utils.py` (if used by multiple modules)
- Private helpers: Inside calling module (e.g., `_apply_view()` in `app.py`)

**Tests:**
- Unit tests for business logic: `tests/test_*.py` (new file for new module or feature)
- Streamlit UI tests: `tests/test_shared_partner.py::TestStreamlitIntegration` (use AppTest)
- Fixtures and helpers: Define at top of test file or `tests/conftest.py` if shared

## Special Directories

**__pycache__:**
- Purpose: Python bytecode cache
- Generated: Yes (automatically by Python)
- Committed: No (in .gitignore)

**.pytest_cache/:**
- Purpose: Pytest test results cache
- Generated: Yes (automatically on test run)
- Committed: No (in .gitignore)

**.git/:**
- Purpose: Git version control metadata
- Generated: Yes (by git init/clone)
- Committed: N/A (Git internal)

**.streamlit/secrets.toml:**
- Purpose: Runtime secrets for Google API access
- Generated: No (manually configured or injected at deployment)
- Committed: No (in .gitignore; never commit secrets)

## Import Organization Pattern

**Order in Source Files:**

1. Standard library imports (e.g., `io`, `datetime`)
2. Third-party imports (e.g., `pandas`, `streamlit`, `gspread`, `google.oauth2`)
3. Local imports (e.g., `from utils import ...`, `from setup_page import ...`)

**Example from app.py (lines 1-6):**
```python
import html                                    # Standard lib
import streamlit as st                         # Third-party
import pandas as pd                            # Third-party
import plotly.express as px                    # Third-party
from utils import generate_excel, ...          # Local
from setup_page import render_setup_page       # Local
```

**Example from utils.py (lines 1-5):**
```python
import pandas as pd                            # Third-party
import io                                      # Standard lib
import streamlit as st                         # Third-party
import gspread                                 # Third-party
from google.oauth2.service_account import ... # Third-party
```

## Module Exports

**app.py:**
- No explicit exports; entry point runs UI directly on `streamlit run app.py`

**setup_page.py:**
- Exports: `render_setup_page()` — called by app.py when setup_complete=False

**utils.py:**
- Exports: `load_excel()`, `extract_categories()`, `load_categories()`, `save_categories()`, `load_category_rules()`, `save_category_rules()`, `calculate_shared_split()`, `write_to_google_sheets()`, `generate_excel()`

**setup_page_harness.py:**
- No exports; test harness only

## Directory Modifications Guidance

**When adding a new tab or feature:**
1. If logic is tab-specific, add directly to `app.py`
2. If logic is reusable, extract to `utils.py` and import
3. Follow existing naming conventions (camelCase functions, lowercase filenames)
4. Add Pytest tests in `tests/test_shared_partner.py` or create new `tests/test_<feature>.py`

**When integrating external services:**
1. Create helper functions in `utils.py` with clear names
2. Use `st.secrets` for credentials (never hardcode)
3. Wrap in try-except with st.warning/st.error fallbacks
4. Test error paths (missing credentials, API failures)

**When modifying data flow:**
1. Keep DataFrame operations in `utils.py` (testable)
2. Keep UI rendering in `app.py` or `setup_page.py`
3. Use `st.session_state` only for state, not for logic
4. Ensure verified_history and other stacks are maintained correctly

---

*Structure analysis: 2026-03-16*
