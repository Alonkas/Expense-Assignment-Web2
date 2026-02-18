# Roommate Expense Manager

A Streamlit web app that helps roommates split and track shared expenses.

## Features

- **Excel Upload** — Import expense files and define partners (roommates) with color-coded labels
- **Shared Expenses** — Optionally designate a "Shared" partner for joint costs that get split evenly
- **Focus Mode** — Card-based verification UI that walks through each expense one-by-one for assignment to a partner and category
- **Table View** — Editable data table for bulk reviewing and editing expenses
- **Final Results** — Summary totals per partner, shared cost splitting, and per-partner Excel downloads
- **Google Sheets Export** — Write results directly to a Google Sheet
- **Dark/Light Mode** — Toggle between dark and light themes

## Getting Started

1. Install dependencies:
   ```
   pip install streamlit pandas openpyxl
   ```
2. Run the app:
   ```
   streamlit run app.py
   ```
3. Upload your expense Excel files, set up partners, and start verifying expenses.
