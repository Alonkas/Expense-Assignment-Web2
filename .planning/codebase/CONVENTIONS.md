# Coding Conventions

**Analysis Date:** 2026-03-16

## Naming Patterns

**Files:**
- Lowercase with underscores: `app.py`, `setup_page.py`, `utils.py`
- Test files follow pytest convention: `test_shared_partner.py` (prefix with `test_`)
- Harness files for testing: `setup_page_harness.py`

**Functions:**
- Lowercase with underscores: `load_excel()`, `extract_categories()`, `calculate_shared_split()`
- Private/internal functions prefixed with underscore: `_apply_view()`, `_get_spreadsheet()`
- Boolean functions named with question phrasing context: `has_shared_partner` (property names), `enable_shared` (parameter names)

**Variables:**
- Lowercase with underscores: `current_partners`, `partner_totals`, `new_expenses`
- Boolean flags prefixed with `has_` or `is_`: `has_shared`, `is_verified`
- Streamlit session state keys use underscore-separated lowercase: `setup_complete`, `verified_history`, `uploader_key`
- Dataframe variables commonly named `df`, `new_df`, `export_df`, `summary_df`

**Types/Classes:**
- Test classes use `Test` prefix: `TestCalculateSharedSplit`, `TestGenerateExcel`, `TestStreamlitIntegration`
- Constants in CAPS: `APP_VERSION = "Ver.4.0.0"`, `default_colors`, `default_names`

## Code Style

**Formatting:**
- No explicit linter/formatter configuration found (no .pylintrc, setup.cfg, pyproject.toml)
- Observed style: 4-space indentation (Python default)
- Line length: Generally pragmatic (no strict limit enforced, some lines exceed 100 chars)
- Blank lines: Single blank line between functions, double between class definitions

**Comments & Section Headers:**
- Section headers use consistent format: `# --- SECTION NAME ---`
- Examples: `# --- CONFIGURATION ---`, `# --- SIDEBAR: LIVE TOTALS & ACTIONS ---`, `# --- FLOW CONTROL ---`
- Inline comments explain "why": `# SAFEGUARD: Ensure we request at least 1 column, max 4`
- Column selection uses inline comments: `# ACTION: ADD FILE`, `# STATE INITIALIZATION`

## Import Organization

**Order:**
1. Standard library: `import html`, `import io`, `import datetime`
2. Third-party packages: `import streamlit as st`, `import pandas as pd`, `import plotly.express as px`
3. Google/external SDKs: `import gspread`, `from google.oauth2.service_account import Credentials`
4. Local imports: `from utils import ...`, `from setup_page import ...`

**Path Aliases:**
- Direct relative imports from root: `from utils import load_excel, extract_categories`
- No path aliases configured; relative imports used throughout

**Example from `app.py`:**
```python
import html
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import generate_excel, calculate_shared_split, write_to_google_sheets, load_category_rules, save_category_rules, load_categories, save_categories
from setup_page import render_setup_page
```

## Error Handling

**Patterns:**
- Broad exception catching: `except Exception as e:` (catches all exceptions)
- Specific gspread exceptions: `except gspread.exceptions.WorksheetNotFound:` (specific resource handling)
- Silent failures on non-critical operations: `except Exception:` with no variable binding (line 129 in utils.py)
- Streamlit alerts for user-facing errors:
  - `st.error()` for critical failures
  - `st.warning()` for non-critical issues
  - `st.info()` for informational messages

**Example from `utils.py` (load_excel):**
```python
def load_excel(file, mapping):
    try:
        df = pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
```

**Nested try-catch pattern for Google Sheets operations:**
```python
def load_categories():
    try:
        spreadsheet = _get_spreadsheet()
        try:
            ws = spreadsheet.worksheet("Categories")
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet("Categories", rows=len(defaults) + 1, cols=1)
            ws.update([["Category"]] + [[c] for c in defaults], value_input_option="USER_ENTERED")
            return defaults
        # ...
    except Exception as e:
        st.warning(f"⚠️ Could not load categories from Google Sheets: {e}")
        return defaults
```

## Logging

**Framework:** `streamlit` (no print statements or logging module observed)

**Patterns:**
- Display progress: `st.progress(done_count / total_count, f"Reviewed: {done_count} / {total_count}")`
- Info alerts: `st.info("💡 Excel suggests this belongs to...")`
- Success messages: `st.success("🎉 All expenses verified and assigned!")`
- Warning messages: `st.warning(f"⚠️ Could not load categories from Google Sheets: {e}")`
- Toast notifications: `st.toast(f"✅ Added {len(new_data)} rows! Upload another or Finish.")`
- Spinner for async operations: `with st.spinner("Writing to Google Sheets..."):`
- Errors: `st.error(f"Error reading file: {e}")`

## Docstrings

**Style:** Single-line docstrings in triple quotes for brief descriptions

**When used:**
- Public utility functions: `load_excel()`, `extract_categories()`, `_get_spreadsheet()`
- Test helper functions: `make_expenses()` — "Build an expenses DataFrame from a list of (partner, amount) tuples."
- Complex business logic: `calculate_shared_split()` — includes multi-line docstring with return value documentation

**Example:**
```python
def extract_categories(df):
    """Extracts unique categories from the loaded dataframe."""
    if 'Category' in df.columns:
        unique_cats = df['Category'].dropna().unique().tolist()
        return [str(c) for c in unique_cats if str(c) != "Uncategorized"]
    return []
```

**Multi-line docstring example (utils.py:calculate_shared_split):**
```python
def calculate_shared_split(df, partners, has_shared_partner):
    """Calculate per-person breakdown including shared expense splitting.

    Returns a dict with:
        individual_totals: {name: amount} for each real partner's own expenses
        shared_total: total of all Shared expenses
        per_person_share: shared_total / number of real partners
        grand_totals: {name: individual + per_person_share}
        real_partners: list of partner names excluding "Shared"
    """
```

## Type Hints

**Usage:** Selective type hints on function parameters and return types where clarity is needed

**Observed patterns:**
- Function parameters: `df: pd.DataFrame`, `view: str`, `partners`, `has_shared_partner` (boolean not always annotated)
- Return types: `-> pd.DataFrame`, `-> dict`, implied when returning objects

**Example from app.py:**
```python
def _apply_view(df: pd.DataFrame, view: str) -> pd.DataFrame:
    if view == "Sum by category":
        return (
            df.groupby("Category", as_index=False)["Amount"]
            .sum()
            .sort_values("Amount", ascending=False)
            .rename(columns={"Amount": "Total"})
        )
```

## Function Design

**Size:** Functions are typically 10-30 lines; UI-heavy functions in `app.py` are longer (40-60 lines due to Streamlit widget density)

**Parameters:**
- Typically 2-4 parameters
- Mapping dictionaries used when many options needed: `mapping = {'date': date_col, 'desc': desc_col, ...}`
- Boolean flags common for feature toggles: `has_shared_partner`

**Return Values:**
- Explicit returns for successful operations
- `None` returned on errors (with user alert via Streamlit)
- Dictionaries returned for multi-value returns: `calculate_shared_split()` returns dict with 5 keys
- DataFrames for transformed data: `load_excel()` returns normalized DataFrame

## Module Design

**Exports:**
- `app.py`: Entry point (Streamlit app), imports from utils and setup_page
- `utils.py`: Utility functions module — exports data loading, Google Sheets operations, Excel generation, shared expense calculation
- `setup_page.py`: UI component module — exports `render_setup_page()` function for reuse
- `setup_page_harness.py`: Test harness — wraps setup_page for testing

**Barrel Files:** None observed; direct imports from specific modules

**Streamlit Session State Management:**
- Initialized in `app.py` and `setup_page_harness.py` with consistent keys
- Session state acts as shared data store across reruns

## Naming Conventions for Streamlit

**Widget Keys:**
- Formatted as `{component}_{index}` or `{action}_{identifier}`: `cat_{curr_idx}`, `btn_{name}_{curr_idx}`, `com_{curr_idx}`
- Unique suffixes to prevent collision: `new_{curr_idx}`, `p_name_{i}`, `p_col_{i}`
- Session state key name reflects purpose: `uploader_key`, `shared_toggle`

**Example from app.py (partner buttons):**
```python
if st.button(label, key=f"btn_{name}_{curr_idx}", type=type_btn, use_container_width=True):
```

---

*Convention analysis: 2026-03-16*
