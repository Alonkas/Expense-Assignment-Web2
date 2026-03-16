# Codebase Concerns

**Analysis Date:** 2026-03-16

## Tech Debt

**Monolithic app.py (485 lines):**
- Issue: Single file contains all UI logic, state management, and view rendering across 5 major tabs
- Files: `app.py`
- Impact: Difficult to test individual features, high complexity per file, hard to locate and fix bugs
- Fix approach: Extract tab logic into separate modules (`tabs/focus_mode.py`, `tabs/table_view.py`, `tabs/results.py`, `tabs/category_rules.py`, `tabs/analytics.py`). Keep app.py as orchestrator only.

**Google Sheets integration tightly coupled (utils.py):**
- Issue: `_get_spreadsheet()` called directly in multiple load/save functions, with identical error handling in each
- Files: `utils.py:60-70`, `utils.py:73-91`, `utils.py:111-130`, `utils.py:133-149`
- Impact: Secrets access duplicated; if GCP API changes, all functions must be updated; no fallback to local storage
- Fix approach: Create `GoogleSheetsClient` class that handles auth once, provides transaction-like API for read/write. Add fallback persistence layer (SQLite or JSON files).

**Broad exception catching without logging:**
- Issue: Multiple `except Exception:` blocks that silently return empty dict or generic warning without stack trace
- Files: `utils.py:129-130` (category rules), `app.py:325-326` (Google Sheets write)
- Impact: Hard to debug what actually failed; production errors hidden from logs
- Fix approach: Use `logging` module instead of bare `except`. Log exception type, message, and traceback to `stderr` or a log file.

**Direct pandas DataFrame mutation in event handlers:**
- Issue: Using `.at[index, column] = value` directly on `st.session_state.expenses` in button callbacks
- Files: `app.py:244-247`, `app.py:155`, `app.py:170`
- Impact: State mutations happen outside of a clear transaction; risk of partial state if operation fails mid-way
- Fix approach: Build immutable update dict, create new DataFrame with `.loc[index] = dict`, or use explicit transaction wrapper.

**No validation on column existence before access:**
- Issue: Accessing column directly (e.g., `df['Verified']`) without checking if it exists first in some code paths
- Files: `app.py:145-146`, `app.py:72-76`
- Impact: Silent KeyError if data is malformed or comes from unexpected source
- Fix approach: Use `df.get('Verified', pd.Series(False))` or explicit `.columns` check at entry points.

## Known Bugs

**Category rules match overrides existing categories without guard:**
- Symptoms: Auto-categorization can override manually-set categories loaded from Excel during table edits
- Files: `app.py:188-193`, `app.py:201-204`
- Trigger: Load expense with category from Excel → Go to Focus Mode → Auto-match tries to override it
- Status: Fixed in commit a5d74c9 (added `pd.notna()` guard), but logic is still complex and fragile
- Safe fix: Explicit rule in code: "If category already set by user (not 'Uncategorized'), do not auto-apply rules. Only suggest."

**Verified column initialization timing:**
- Symptoms: If 'Verified' column doesn't exist, it's created at line 146 but might be missing if data comes from certain paths
- Files: `app.py:145-146`
- Trigger: Fast data reloads or concurrent access via multiple tabs
- Workaround: Always ensure Verified column in `load_excel()` (currently done at line 47 in utils.py)
- Fix approach: Add `ensure_verified_column()` utility function called at all DataFrame creation points.

**Empty string category names not validated:**
- Symptoms: User can save "" or "   " as category name, creating invisible options in dropdowns
- Files: `app.py:215-218` (Save Cat button), `app.py:294-298` (Table View)
- Trigger: Click "Save Cat" with empty input
- Workaround: Frontend validation exists (`new_cat.strip()`) but not enforced at all entry points
- Fix approach: Create `validate_category_name(name: str) -> str` that enforces min length, no whitespace-only, no duplicates.

**Index out of bounds if selectbox has no matching option:**
- Symptoms: If current category not in categories list, selectbox default index calculation fails gracefully but silently
- Files: `app.py:209`
- Trigger: Delete a category from Google Sheets → expenses still reference it → Focus Mode crashes
- Impact: User loses ability to verify expenses
- Fix approach: Pre-filter categories in setup to ensure all expense categories are in `st.session_state.categories`, or add fallback option "Deleted Category (keep as-is)".

## Security Considerations

**HTML injection via user input (PATCHED):**
- Risk: User description/comment rendered with `unsafe_allow_html=True` could execute JavaScript
- Files: `app.py:110`, `app.py:178`, `app.py:450`
- Current mitigation: `html.escape()` wrapper applied to all user inputs (verified in code)
- Status: Fixed in commit 6fda15b
- Recommendations: Maintain escaping; add lint check to prevent `unsafe_allow_html` without escape.

**Google Sheets API credentials in code:**
- Risk: `st.secrets["gcp_service_account"]` accessed directly without validation
- Files: `utils.py:66-70`
- Current mitigation: Secrets stored in `.streamlit/secrets.toml` (git-ignored), not in code
- Impact: If `.streamlit/secrets.toml` leaks, attacker gets full GCP access including all spreadsheets
- Recommendations: Use GCP service account with minimal scopes (already done: only sheets + drive). Rotate credentials quarterly. Monitor GCP activity logs.

**No input sanitization on Excel column names:**
- Risk: Attacker uploads Excel with columns named like SQL injection (`'); DROP TABLE--`)
- Files: `utils.py:14-28`
- Current mitigation: Only expected columns are renamed; excess columns ignored
- Impact: Low risk since rename_dict is hardcoded, not dynamic SQL
- Recommendations: Validate column names match expected pattern (alphanumeric + spaces).

**Spreadsheet URL exposed in success message:**
- Risk: `return spreadsheet.url` gives full Google Sheets URL which could be shared/intercepted
- Files: `utils.py:247`
- Current mitigation: Only shown to logged-in Streamlit app user in their browser
- Recommendations: No change needed unless URL should be kept private.

## Performance Bottlenecks

**Google Sheets API round-trip on every app load:**
- Problem: `load_categories()` and `load_category_rules()` call `_get_spreadsheet()` on every session startup
- Files: `app.py:21`, `app.py:25`
- Cause: No caching; full worksheet fetch every reload
- Severity: Low for small datasets, becomes noticeable with 1000+ category rules
- Improvement path:
  - Add 5-minute TTL cache using `@st.cache_data(ttl=300)` decorator
  - Or use browser-side storage for categories (save to `.streamlit/client_state.json`)
  - Or pre-load once on startup and only sync on save

**DataFrame comparison with `.equals()` on large datasets:**
- Problem: `edited.equals(view_df)` at line 277 does full recursive equality check
- Files: `app.py:277`, `app.py:395`
- Cause: Checking if user changed anything before updating; `equals()` is O(n)
- Severity: Acceptable for <10k rows, noticeable UI stutter for >50k rows
- Improvement path: Track which cells changed instead of comparing whole DataFrames; use `edited.compare(view_df)` for diff instead.

**Excel generation with xlsxwriter on every download:**
- Problem: `generate_excel()` rebuilds full Excel file every download; column width calculation is O(n)
- Files: `utils.py:250-290`
- Cause: xlsxwriter doesn't cache; width calculation loops over all data
- Severity: OK for <5k rows, noticeable delay for >50k rows
- Improvement path: Cache Excel bytes; memoize column widths; use openpyxl instead if dynamic updates needed.

**No pagination in Table View editor:**
- Problem: st.data_editor loads entire DataFrame; renders all rows
- Files: `app.py:265-289`
- Cause: Streamlit's data_editor doesn't have built-in pagination
- Severity: Browser freezes/OOM with >20k rows
- Improvement path: Add pagination controls; show 500 rows at a time; or use ag-Grid wrapper (streamlit-aggrid).

## Fragile Areas

**Focus Mode state machine (unverified → verified flow):**
- Files: `app.py:142-256`
- Why fragile: Complex state tracking with `verified_history` stack; multiple `st.rerun()` calls; index tracking across mutations
- Risk: "Go Back" button can corrupt state if user re-orders rows or deletes rows before using it
- Safe modification: Refactor to explicit state machine class with pre/post conditions checked before each transition. Add assertions for invariants (verified count == len(verified_history)).
- Test coverage: Good (tests in `test_shared_partner.py:283-335`), but missing edge cases like rapid button clicks.

**Category rules auto-learning logic:**
- Files: `app.py:250-252`
- Why fragile: Saves rule after EVERY verification; no deduplication; can create rules for similar descriptions
- Risk: Category rules bloat over time; "Walmart #123" and "Walmart #456" become separate rules
- Safe modification: Add rule normalization step (fuzzy match on description; only save if confidence >80%). Or limit rule count to 1000.
- Test coverage: None (no tests for auto-learning rules creation).

**Table View auto-save with row insertion/deletion:**
- Files: `app.py:277-289`
- Why fragile: Logic assumes indices are stable; `st.data_editor` with `num_rows="dynamic"` allows user to delete/insert rows
- Risk: If user adds row, then deletes another row, index alignment breaks; `reindex(edited.index, fill_value=False)` may not preserve intended Verified status
- Safe modification: Require explicit save button instead of auto-save; or use row IDs instead of indices.
- Test coverage: None (no tests for dynamic row operations).

**Partner and category initialization order:**
- Files: `app.py:18-25`, `setup_page.py:9-47`
- Why fragile: Partners must be set before expenses can be verified; categories loaded asynchronously from Google Sheets; race conditions possible
- Risk: User clicks "Finish" before categories are loaded; uses partner from old session; etc.
- Safe modification: Add explicit validation at start of main app: `assert st.session_state.partners`, `assert st.session_state.categories`; block access until satisfied.
- Test coverage: Partial (Streamlit testing harness tests some flows but not all edge cases).

## Scaling Limits

**In-memory DataFrame for all expenses:**
- Current capacity: ~50k rows comfortably, ~500k rows with memory pressure
- Limit: Laptop with 8GB RAM maxes out around 1M rows of mixed-type data
- Scaling path:
  - For <100k: Current approach acceptable
  - For 100k-1M: Implement server-side SQLite database, load by date range on demand
  - For >1M: Use BigQuery or Postgres; implement pagination; lazy-load only visible rows

**Google Sheets API rate limits:**
- Current capacity: ~100 read/write operations per minute (GCP default)
- Limit: If user uploads 10 files in rapid succession, hits rate limit
- Scaling path: Queue uploads to batch process; implement exponential backoff + retry logic.

**Plotly pie chart generation:**
- Current capacity: ~500 categories before chart renders slowly
- Limit: >1000 categories → browser struggles with DOM rendering
- Scaling path: Use server-side pie rendering (Pillow → PNG); or limit pie chart to top 20 categories + "Other".

## Dependencies at Risk

**google-auth dependency:**
- Risk: Google deprecates OAuth2 flow; Credentials API changes
- Impact: Google Sheets integration breaks
- Migration plan: Abstract auth behind interface; prepare fallback to API key (read-only) if service account fails.

**Streamlit <1.40:**
- Risk: Using `unsafe_allow_html` is intentional but risky; future Streamlit versions may sandbox this further
- Impact: Custom styling (dark theme CSS) may break
- Migration plan: Use official Streamlit theming APIs (now available in 1.40+); eliminate CSS hacks.

**openpyxl vs xlsxwriter:**
- Risk: Project uses both libraries; could conflict on .xlsx format
- Impact: Generated Excel files may be incompatible with older Excel versions
- Migration plan: Standardize on one; recommend xlsxwriter (lighter, faster) for generation; openpyxl (richer API) for reading.

## Missing Critical Features

**No backup/recovery mechanism:**
- Problem: All data lives in Google Sheets; no local backup
- Blocks: User data loss if Google account compromised or deleted
- Fix: Add local SQLite export on every save; or GitHub Gist backup.

**No audit trail:**
- Problem: Cannot see who changed what expense when
- Blocks: Multi-user scenarios; debugging incorrect categorizations
- Fix: Add `audit_log` table with (timestamp, user, field, old_value, new_value) tuples.

**No bulk categorization:**
- Problem: If 500 expenses import without categories, user must verify each one manually (30+ minutes)
- Blocks: Fast onboarding for large datasets
- Fix: Add "Bulk assign by partner" or "Bulk assign by date range" UI.

**No data validation rules:**
- Problem: User can enter negative amounts, future dates, invalid partners
- Blocks: Data integrity; incorrect calculations
- Fix: Add JSON schema validation on load_excel; enforce constraints in UI.

**No export to other formats:**
- Problem: Only Excel + Google Sheets; no CSV, PDF, or accounting software (QuickBooks) support
- Blocks: Integration with other financial tools
- Fix: Add CSV/PDF export; consider QuickBooks API integration.

## Test Coverage Gaps

**Auto-categorization edge cases:**
- What's not tested: Handling when matched category doesn't exist in categories list; what happens if rule has empty category value
- Files: `app.py:188-204`
- Risk: Silent fallback to "Uncategorized" without warning; user doesn't know why rule didn't apply
- Priority: High (causes silent data loss of category intent)

**Multi-file merge logic:**
- What's not tested: Merging expenses with different schemas (one file has "Partner" column, other doesn't); duplicate rows from same file
- Files: `setup_page.py:102`
- Risk: Subtle data corruption when concatenating DataFrames with misaligned indices
- Priority: High (user may not notice duplicates)

**Error handling in Google Sheets operations:**
- What's not tested: Network timeout; permission denied; quota exceeded; worksheet already exists
- Files: `utils.py:73-149`
- Risk: App hangs or crashes with cryptic error message
- Priority: Medium (users can retry, but UX is poor)

**Category rules persistence:**
- What's not tested: Saving rules with special characters; very long descriptions (>255 chars); Unicode edge cases
- Files: `utils.py:133-149`, `app.py:250-252`
- Risk: Rules fail to save silently; or save incorrectly and cause lookup mismatches
- Priority: Medium (edge case but data loss risk)

**Date handling in different locales:**
- What's not tested: User in Japan uploads Excel with dates as YYYY/MM/DD; current code assumes dayfirst=True
- Files: `utils.py:40`
- Risk: Dates parsed incorrectly; expense assigned to wrong month
- Priority: Medium (low likelihood but high impact when it happens)

---

*Concerns audit: 2026-03-16*
