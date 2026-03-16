# Architecture

**Analysis Date:** 2026-03-16

## Pattern Overview

**Overall:** Streamlit-based web application with layered separation between UI rendering, business logic, and data persistence.

**Key Characteristics:**
- Session-state driven reactive UI model (Streamlit)
- Functional business logic layer independent of UI framework
- Google Sheets integration for persistent storage
- Multi-step wizard flow (setup → verification → reporting)
- Pandas-powered data transformations and reporting

## Layers

**Presentation (UI):**
- Purpose: Render interactive UI components and handle user interactions
- Location: `app.py`, `setup_page.py`
- Contains: Streamlit page layouts, tabs, forms, buttons, data editors
- Depends on: `utils.py` (business logic), `st.session_state` (state)
- Used by: End users via web browser

**Business Logic:**
- Purpose: Core calculations, data transformations, and rules engine
- Location: `utils.py` (core functions), imported by presentation layer
- Contains: `calculate_shared_split()`, `generate_excel()`, category rule matching, data loading/saving
- Depends on: Pandas, gspread (Google Sheets client), openpyxl (Excel)
- Used by: Both presentation layer and tests

**Data Persistence:**
- Purpose: Load from and save to Google Sheets; import/export Excel
- Location: `utils.py` (functions: `load_categories()`, `save_categories()`, `load_category_rules()`, `save_category_rules()`, `write_to_google_sheets()`)
- Contains: Google Sheets API integration, file I/O for Excel
- Depends on: gspread, Google OAuth2 credentials via `st.secrets`
- Used by: UI layer on-demand, during setup and export

**State Management:**
- Purpose: Hold application state across page reruns
- Location: `st.session_state` (initialized in `app.py` lines 14-27)
- Contains: expenses (DataFrame), partners (dict), categories (list), category_rules (dict), has_shared_partner (bool), verified_history (list), setup_complete (bool)
- Depends on: Streamlit session lifecycle
- Used by: All UI components and business logic

## Data Flow

**Setup Flow (Setup Page):**
1. User defines roommates/partners with colors → stored in `st.session_state.partners`
2. User uploads Excel files with column mapping
3. `load_excel()` reads file, normalizes columns, cleans data
4. Categories extracted via `extract_categories()` → stored in `st.session_state.categories`
5. Data appended to `st.session_state.expenses` (DataFrame)
6. `setup_complete=True` → triggers dashboard view

**Verification Flow (Focus Mode Tab):**
1. Get first unverified expense from DataFrame (Verified=False)
2. Display expense card with date, description, amount
3. User selects partner and category (with auto-category suggestion from category_rules)
4. On confirm: update DataFrame row, set Verified=True, push index to verified_history
5. Save category rule to Google Sheets if new mapping
6. Rerun → get next unverified expense

**Reporting Flow (Final Results Tab):**
1. User clicks "Download Combined Report" → `generate_excel()` creates Excel with Expenses + Summary sheets (if shared partner enabled)
2. User clicks "Write to Google Sheets" → `write_to_google_sheets()` clears and rewrites All Expenses + Summary sheets
3. User views analytics charts by partner → `_apply_view()` transforms DataFrame by view type (raw, by category, by date, etc.)

**State Management:**
- Streamlit reruns page on every interaction (button click, form change)
- `st.session_state` persists across reruns within a session
- On first page load, state is initialized if keys don't exist (lines 14-27)
- Analytics data queries directly from `st.session_state.expenses` (live DataFrame)

## Key Abstractions

**Expense DataFrame:**
- Purpose: Central data structure for all expenses
- Examples: `st.session_state.expenses`
- Pattern: Pandas DataFrame with columns [Date, Description, Amount, Partner, Category, Comment, Verified]
- Lifecycle: Created during setup, modified during verification, exported for reporting

**Partner Configuration:**
- Purpose: Map roommate names to display colors
- Examples: `st.session_state.partners = {'Alice': '#FF4B4B', 'Bob': '#1E90FF', 'Shared': '#808080'}`
- Pattern: Dict[str, str] where key=name, value=hex color
- Lifecycle: Set once at setup, toggleable "Shared" for joint expenses

**Category Rules Engine:**
- Purpose: Auto-suggest categories based on exact expense description match
- Examples: `st.session_state.category_rules = {'walmart supermarket': 'Groceries', 'shell gas': 'Fuel'}`
- Pattern: Dict[str, str] where key=lowercased full description, value=category name
- Lifecycle: Pre-loaded from Google Sheets, auto-learned on verification (line 250-252), user-editable in Category Rules tab

**Shared Expense Split:**
- Purpose: Calculate per-partner breakdown when expenses are marked "Shared"
- Examples: `calculate_shared_split()` returns dict with individual_totals, shared_total, per_person_share, grand_totals
- Pattern: Pure function that filters DataFrame by Partner, sums by person, divides shared equally
- Lifecycle: Called on-demand during reporting and Google Sheets export

## Entry Points

**Main Application:**
- Location: `app.py`
- Triggers: `streamlit run app.py`
- Responsibilities:
  - Initialize session state (lines 14-27)
  - Render dark theme CSS (lines 33-45)
  - Display version badge (lines 48-57)
  - Route to setup_page if `setup_complete=False` (lines 82-83)
  - Render main dashboard with 5 tabs if setup complete (lines 85-486)

**Setup Page (Conditional):**
- Location: `setup_page.py` / `render_setup_page()`
- Triggers: Called from app.py when `setup_complete=False`
- Responsibilities:
  - Step 1: Partner definition UI (lines 8-47)
  - Step 2: Multi-file Excel upload with column mapping (lines 51-110)
  - Step 3: Progress display and finish button (lines 112-125)

**Setup Page Harness (Testing):**
- Location: `setup_page_harness.py`
- Triggers: `streamlit run setup_page_harness.py` (for testing setup flow in isolation)
- Responsibilities: Initialize minimal session state and render setup_page for testing

## Error Handling

**Strategy:** Try-except blocks with user-facing Streamlit messages (st.error, st.warning, st.info)

**Patterns:**
- **File Loading:** `load_excel()` catches read errors, returns None, UI displays st.error (lines 8-12)
- **Google Sheets Access:** Functions wrapped in try-except, fallback to defaults or warnings (lines 76-91, 129-130)
- **Data Validation:** Numeric coercion with fillna(0.0), date parsing with dayfirst=True, category fillna("Uncategorized") (lines 39-45)
- **UI State Safety:** Checks for empty partners list before rendering buttons, prevents crash (lines 254-255)

## Cross-Cutting Concerns

**Logging:**
- No explicit logging framework; uses Streamlit messages (st.info, st.warning, st.error, st.success, st.toast)
- Example: "✅ Added {len(new_data)} rows! Upload another or Finish." (line 106)

**Validation:**
- Excel column mapping validated on file load (required: Date, Description, Amount)
- Partner names required before proceeding past setup
- Category selection validated against loaded categories list
- Numeric amounts coerced to float with error handling

**Authentication:**
- Google Sheets access via Service Account credentials in `st.secrets["gcp_service_account"]`
- No user login required; single shared Google Sheet per deployment
- Spreadsheet ID stored in `st.secrets["gcp_service_account"]["spreadsheet_id"]`

**State Isolation:**
- Each Streamlit session maintains its own `st.session_state` object
- No cross-session state sharing; suitable for single-user per browser tab
- Session persists until browser tab closed or explicit "Reset All Data"

---

*Architecture analysis: 2026-03-16*
