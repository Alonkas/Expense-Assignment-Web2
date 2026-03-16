# External Integrations

**Analysis Date:** 2026-03-16

## APIs & External Services

**Google Sheets API:**
- Google Sheets - Core backend for persisting categories and category rules
  - SDK/Client: `gspread` (Python client library)
  - Auth: Service account credentials from `st.secrets["gcp_service_account"]`
  - Scope: `https://www.googleapis.com/auth/spreadsheets`, `https://www.googleapis.com/auth/drive`
  - Spreadsheet ID: Stored in `st.secrets["gcp_service_account"]["spreadsheet_id"]`

## Data Storage

**Databases:**
- Google Sheets (primary persistent storage)
  - Connection: Service account authentication
  - Client: `gspread.Spreadsheet` object
  - Worksheets:
    - `Categories` - List of available expense categories (defaults: Groceries, Fuel, Electricity, Internet, Rent, Insurance, Dining Out)
    - `Category Rules` - Description-to-category mapping rules (auto-categorization hints)
    - `All Expenses` - Complete expense data exported from app
    - `Summary` - Per-partner totals (individual, shared split, grand totals)

**File Storage:**
- Local Excel files (.xlsx) - User-uploaded expense files
  - Format: Standard Excel with Date, Description, Amount columns (plus optional Partner, Category, Comment)
  - Handling: `openpyxl` for reading, `xlsxwriter` for writing exports
- In-Memory Session State: Streamlit `st.session_state` for runtime expense DataFrame
  - Not persisted between sessions (Streamlit Cloud resets state on reconnect)

**Caching:**
- Streamlit built-in caching (via implicit session state)
  - No external caching service
  - Session-scoped data stored in `st.session_state`

## Authentication & Identity

**Auth Provider:**
- Google Cloud Platform (GCP) Service Account
  - Implementation: Service account key file in `st.secrets["gcp_service_account"]`
  - Credentials file format: JSON (service account credentials)
  - Used for: Google Sheets API authentication
  - Library: `google.oauth2.service_account.Credentials`
  - No user authentication (app is single-user tool per instance)

**Implementation Details:**
- `_get_spreadsheet()` function in `utils.py` (lines 60-70):
  - Loads service account from `st.secrets["gcp_service_account"]`
  - Creates Credentials object with spreadsheets and drive scopes
  - Opens Google Sheet by ID stored in secrets
  - Returns gspread Spreadsheet object for all subsequent operations

## Monitoring & Observability

**Error Tracking:**
- None - Basic try/except with `st.error()` and `st.warning()` for user-facing errors

**Logs:**
- Streamlit logs (stdout/stderr from `streamlit run`)
- No structured logging or external log aggregation
- Warning messages displayed in UI for:
  - Category loading failures from Google Sheets
  - Category rules loading failures from Google Sheets
  - Category saving failures to Google Sheets
  - Category rules saving failures to Google Sheets

## CI/CD & Deployment

**Hosting:**
- Designed for Streamlit Cloud deployment (typical pattern)
- Can run on: Any machine with Python 3.7+, or Docker container with Python runtime

**CI Pipeline:**
- None detected (no GitHub Actions, GitLab CI, or similar configuration)

**Testing:**
- pytest framework available (`.pytest_cache/` present)
- Test files exist in `tests/` directory
- No CI integration for automated testing

## Environment Configuration

**Required Environment Variables (via Streamlit secrets):**
- `gcp_service_account` - JSON object containing:
  - `type`, `project_id`, `private_key_id`, `private_key`, `client_email`, `client_id`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`, `client_x509_cert_url` (standard GCP service account fields)
  - `spreadsheet_id` - Google Sheet ID to sync categories/rules to

**Secrets Location:**
- Local development: `.streamlit/secrets.toml`
- Streamlit Cloud: Secrets stored in Streamlit Cloud app dashboard
- Note: `.streamlit/secrets.toml` should be in `.gitignore` (not checked in to version control)

**Configuration Files:**
- `.streamlit/config.toml` - Streamlit app configuration (theme: dark)

## Webhooks & Callbacks

**Incoming:**
- None - App is pull-based (user uploads files, app reads them)

**Outgoing:**
- Google Sheets write operations (via gspread API calls):
  - `write_to_google_sheets()` in `utils.py` (lines 196-247) - Exports all expenses and summary to Google Sheet
  - `save_categories()` in `utils.py` (lines 94-108) - Writes categories list to Categories worksheet
  - `save_category_rules()` in `utils.py` (lines 133-149) - Writes description→category mapping rules to Category Rules worksheet

## Data Flow

**Category Sync Pipeline:**
1. App startup: `load_categories()` reads from Google Sheets Categories worksheet
2. User adds/edits categories in UI
3. On save: `save_categories()` writes updated list to Google Sheets
4. Fallback: If Google Sheets unavailable, uses hardcoded defaults

**Category Rules Sync Pipeline:**
1. App startup: `load_category_rules()` reads from Google Sheets Category Rules worksheet
2. Rule engine applies rules to description field for auto-categorization (with `pd.notna()` guard)
3. User can verify/override category per expense
4. On final export: `save_category_rules()` writes updated rules to Google Sheets
5. Fallback: If Google Sheets unavailable, no rules loaded (empty dict)

**Expense Export Flow:**
1. User uploads Excel file(s) with expenses
2. `load_excel()` reads file and maps columns
3. Data processed in-memory (pandas DataFrame)
4. User verifies and assigns partners/categories
5. On export: `write_to_google_sheets()` creates/updates worksheets:
   - All Expenses - Full expense list
   - Summary - Per-partner totals with shared cost breakdown
6. Download option: `generate_excel()` creates local Excel file for download

---

*Integration audit: 2026-03-16*
