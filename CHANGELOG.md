# Changelog

All notable changes to the Roommate Expense Manager are documented here.

---

## Ver.5.0.0
- **Security cleanup** — Removed personal expense data (`data/categories.csv`, `data/category_rules.csv`) from git tracking; files are now generated at runtime and gitignored
- **Untracked build artifacts** — Removed committed `__pycache__/*.pyc` files and `.claude/settings.local.json` from repo
- **Updated `.gitignore`** — Added rules for user data files, Python cache, and local IDE settings

---

## Ver.4.7.0
- **Settings tab** — Renamed "Category Rules" to "Settings" and moved it to the last tab position (after Analytics)
- **External editing** — Removed in-app rule editing (Edit/Save/Cancel, Add New Rule); added "Open in Excel" button to edit the local `data/category_rules.csv` directly, with a Reload button to refresh after changes

---

## Ver.4.6.0
- **Streamlined setup wizard** — Removed the "Setup Complete" confirmation step; after confirming partners, the app goes directly to the Expense Dashboard

---

## Ver.4.5.0
- **Hebrew CSV fix** — CSV files (`categories.csv`, `category_rules.csv`) now written with UTF-8 BOM so Hebrew displays correctly when opened in Excel
- **Local category storage** — Categories and category rules now saved to local CSV files (`data/categories.csv`, `data/category_rules.csv`) instead of Google Sheets
- **Google Sheets grid fix** — Resize worksheets before updating to prevent grid limits error when reused sheets have fewer rows/columns than new data

---

## Ver.4.4.0
- **Category Summary tab** — New tab with per-partner sub-tabs showing category breakdowns (amount + % of total), a total row, and a Plotly pie chart

---

## Ver.4.3.0
- **Per-partner Excel tabs** — Combined Report now includes a dedicated sheet per partner (and Shared) with filtered expenses and a bold Total sum row
- **Per-partner Google Sheets tabs** — Same per-partner breakdown when exporting to Google Sheets, with bold Total row formatting

## Ver.4.2.1
- **Bug fix** — `pd.notna` guard on category rules to prevent NaN keys from crashing auto-categorization
- **Bug fix** — Prevent category rules from overriding categories already assigned in Excel or Table View

## Ver.4.2.0
- **Bug fix** — Table View edits now properly reflect in Focus Mode (clear cached widget state on save)

## Ver.4.1.0
- **Source (Credit Card) column** — New optional "Source" column detected during setup and displayed on expense cards in Focus Mode
- **Per-partner shared split toggle** — Each partner can individually opt in/out of sharing Shared expenses

## Ver.4.0.0
- **Analytics tab** — New tab with per-partner sub-tabs showing expenses in multiple views (raw table, sum by category, by date, most expensive, pie chart)
- **Plotly pie charts** — Category breakdown visualized as interactive pie charts
- **Sum totals** — Running sums displayed below each table view in Analytics
- **New dependency** — `plotly` added to requirements

## Ver.3.9.0
- **Table View editing** — Editable data table with dynamic rows for bulk expense management
- **Always-dark theme** — Removed dark/light toggle; app now enforces dark mode via custom CSS

## Ver.3.8.0
- **Currency cleanup** — Removed `$` currency symbols from all displayed amounts for locale-neutral formatting
- **Code quality** — Fixed XSS vulnerabilities (escaped all user data in HTML), fixed silent save failures in Google Sheets functions, general code review fixes

## Ver.3.7.0
- **Category system** — Categories loaded from and saved to Google Sheets ("Categories" tab)
- **Category Rules** — Auto-learned description-to-category mappings stored in Google Sheets ("Category Rules" tab), applied automatically during Focus Mode verification
- **Editable rules table** — Category Rules tab with inline editing synced to Google Sheets

## Ver.3.3.0
- **Dark Mode** — Added dark/light theme toggle with custom CSS styling
- **Google Sheets export** — Write expense data and summary directly to a configured Google Sheet

## Ver.3.2.4
- **Shared expenses** — Added Shared partner sum and per-person split in Final Results

## Ver.3.2.2
- **Initial release** — Excel upload, partner setup, Focus Mode verification, Table View, Final Results with per-partner totals and Excel downloads
