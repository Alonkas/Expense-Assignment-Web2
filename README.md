# Roommate Expense Manager

A Streamlit web app that helps roommates split and track shared expenses. Upload Excel files, assign each expense to a partner, categorize them, and export polished reports to Excel or Google Sheets.

## Features

### Setup Wizard
- **Excel Upload** — Import `.xlsx` / `.xls` expense files with automatic column detection (supports Hebrew and English headers)
- **Column Mapping** — Auto-detects Date, Description, Amount, Source, Partner, Category, and Comment columns; lets you override manually
- **Partner Configuration** — Auto-discovers partners from data or lets you create them manually with custom colors
- **Shared Partner** — Optionally enable a "Shared" partner for joint expenses, with per-partner opt-in/out of the shared split
- **Add More Files** — Import additional files without losing existing data or partner setup

### Dashboard Tabs

#### Focus Mode (Verification)
- Card-based UI that walks through each unverified expense one-by-one
- Shows date, description, amount, and source (credit card) on a styled card
- Color-coded partner buttons for quick assignment
- Pre-filled partner suggestions highlighted with a confirm button
- Category selector with auto-learned rules and inline "Add New" option
- Comment field per expense
- Progress bar and Go Back button for navigation

#### Table View
- Full editable data table with dropdown selectors for Partner and Category
- Add/remove rows dynamically
- Save Changes button syncs edits back to Focus Mode
- Add new categories inline

#### Final Results
- Per-partner total metrics with shared split breakdown (individual totals, shared total, per-person share, grand totals)
- **Download Combined Report** — Excel file with:
  - "Expenses" sheet (all data)
  - "Summary" sheet (shared split breakdown)
  - Per-partner sheets (filtered rows + bold Total sum row)
- **Write to Google Sheets** — Same structure pushed to a configured Google Sheet
- Per-partner individual Excel download buttons

#### Category Rules
- Auto-learned description-to-category mappings (learned during verification)
- Editable table synced to Google Sheets
- Rules are applied automatically in Focus Mode for matching descriptions

#### Analytics
- Per-partner sub-tabs with multiple view modes:
  - Raw table, Sum by category, By date (newest first), Most to least expensive
  - Pie chart by category (Plotly)
- Sum totals displayed below each table
- Shared expenses shown alongside each real partner's data

### Sidebar
- Live running totals per partner with color-coded cards
- Shared split preview (per-person share from Shared)
- Add More Files and Reset All Data buttons

### Other
- Always-dark theme with custom CSS
- Version badge displayed at bottom-left
- XSS-safe HTML rendering (all user data escaped)
- Google Sheets integration for categories, category rules, and full report export

## Getting Started

### Prerequisites
- Python 3.10+
- A Google Cloud service account (for Google Sheets features)

### Installation
```bash
pip install -r requirements.txt
```

### Dependencies
- `streamlit` — Web framework
- `pandas` — Data processing
- `openpyxl` — Excel file reading
- `xlsxwriter` — Excel file writing
- `plotly` — Analytics charts
- `gspread` + `google-auth` — Google Sheets integration

### Running
```bash
streamlit run app.py
```

### Google Sheets Setup
Add a `.streamlit/secrets.toml` file with your service account credentials:
```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "..."
token_uri = "..."
spreadsheet_id = "YOUR_GOOGLE_SHEET_ID"
```

## Project Structure
```
app.py           — Main Streamlit app (dashboard, tabs, sidebar)
setup_page.py    — Setup wizard (upload, mapping, partners)
utils.py         — Data processing, Excel/Google Sheets export, category management
run.bat          — Windows launcher script
requirements.txt — Python dependencies
```
