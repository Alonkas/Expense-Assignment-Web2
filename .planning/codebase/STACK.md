# Technology Stack

**Analysis Date:** 2026-03-16

## Languages

**Primary:**
- Python 3.13+ - Core application language for all business logic and utilities

## Runtime

**Environment:**
- Python 3.13.5 (detected in environment)
- Minimum: Python 3.7+ (based on dependency compatibility)

**Package Manager:**
- pip - Standard Python package manager
- Lockfile: `requirements.txt` (present, no poetry.lock or pipenv lockfile)

## Frameworks

**Core:**
- Streamlit 1.x - Web UI framework for the expense management application
  - Purpose: Interactive dashboard and form-based UI for expense tracking
  - Config: `.streamlit/config.toml`

**Data Processing:**
- pandas - DataFrame manipulation and Excel file handling
  - Purpose: Loading, cleaning, transforming expense data from Excel files

**Visualization:**
- plotly - Interactive charts and pie charts
  - Purpose: Analytics visualization (pie charts for expense breakdown)

**Excel I/O:**
- openpyxl - Reading/writing Excel (.xlsx) files
  - Purpose: Importing expense data from Excel files
- xlsxwriter - Creating formatted Excel output files
  - Purpose: Generating summary Excel downloads with formatted sheets

**Google Sheets Integration:**
- gspread - Google Sheets Python client library
  - Purpose: Reading/writing categories and category rules to Google Sheets
- google-auth - Google authentication for service account credentials
  - Purpose: Service account authentication for Google Sheets API access

## Key Dependencies

**Critical:**
- streamlit - Web framework (core to entire application)
- pandas - Data manipulation (all expense processing relies on this)
- gspread - Google Sheets integration (categories and rules sync)
- google-auth - Authentication provider (blocks Google Sheets integration if missing)

**Infrastructure:**
- openpyxl - Excel import capability (alternative to xlrd for newer Excel files)
- xlsxwriter - Excel export capability (summary generation)
- plotly - Charting for analytics view

**Data Validation:**
- Python standard library (pandas.to_numeric, datetime handling) - No external validation library

## Configuration

**Environment:**
- Theme: Dark mode enforced (configuration in `app.py` via CSS styling)
- Streamlit config: `.streamlit/config.toml`
  - Sets base theme to "dark"
- Secrets management: `.streamlit/secrets.toml` (local development)
  - Contains: `gcp_service_account` dict with service account credentials
  - Contains: `spreadsheet_id` field within gcp_service_account

**Build:**
- No build system (pure Python Streamlit app)
- No bundler or compiler configuration

## Platform Requirements

**Development:**
- Windows/macOS/Linux with Python 3.7+
- Streamlit CLI (`streamlit run app.py`)
- Launcher script: `run.bat` (Windows batch script that validates Python and dependencies)

**Production:**
- Streamlit Cloud deployment (typical for Streamlit apps)
  - Or: Self-hosted via Docker/VM running Python and Streamlit
  - Requires: Python 3.7+, all dependencies from `requirements.txt`
  - Requires: `.streamlit/secrets.toml` with GCP service account credentials

**External Dependencies:**
- Google Cloud Platform (GCP) - For Google Sheets API access
- Google Sheets - Backend for categories and category rules persistence

## Deployment

**Application Entry Point:**
- `app.py` - Main Streamlit application

**Startup Command:**
```bash
streamlit run app.py
```

**Windows Launcher:**
- `run.bat` - Batch script that checks Python installation, installs dependencies, and launches app

---

*Stack analysis: 2026-03-16*
