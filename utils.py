import pandas as pd
import io
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def load_excel(file, mapping):
    try:
        df = pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

    # Rename columns
    rename_dict = {
        mapping['date']: 'Date',
        mapping['desc']: 'Description',
        mapping['amt']: 'Amount'
    }
    
    if mapping.get('partner') and mapping['partner'] != "None":
        rename_dict[mapping['partner']] = 'Partner'
    if mapping.get('cat') and mapping['cat'] != "None":
        rename_dict[mapping['cat']] = 'Category'
    if mapping.get('comment') and mapping['comment'] != "None":
        rename_dict[mapping['comment']] = 'Comment'

    df = df.rename(columns=rename_dict)
    
    # Normalize Columns
    expected_cols = ['Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    df = df[expected_cols]

    # --- CLEANING DATA ---
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0.0)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
    df = df.dropna(subset=['Date'])
    
    df['Partner'] = df['Partner'].replace(["", " ", "nan"], None)
    df['Category'] = df['Category'].fillna("Uncategorized")
    df['Comment'] = df['Comment'].fillna("")

    df['Verified'] = False

    return df

def extract_categories(df):
    """Extracts unique categories from the loaded dataframe."""
    if 'Category' in df.columns:
        # Get unique values, drop None/NaN, convert to list
        unique_cats = df['Category'].dropna().unique().tolist()
        # Remove "Uncategorized" if it exists so we don't duplicate it
        return [str(c) for c in unique_cats if str(c) != "Uncategorized"]
    return []

def _get_spreadsheet():
    """Return the configured gspread Spreadsheet object."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(st.secrets["gcp_service_account"]["spreadsheet_id"])


def load_categories():
    """Load categories list from the 'Categories' Google Sheet tab."""
    defaults = ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]
    try:
        spreadsheet = _get_spreadsheet()

        try:
            ws = spreadsheet.worksheet("Categories")
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet("Categories", rows=len(defaults) + 1, cols=1)
            ws.update([["Category"]] + [[c] for c in defaults], value_input_option="USER_ENTERED")
            return defaults

        records = ws.get_all_records()
        categories = [str(row.get("Category", "")).strip() for row in records if str(row.get("Category", "")).strip()]
        return categories if categories else defaults
    except Exception as e:
        st.warning(f"⚠️ Could not load categories from Google Sheets: {e}")
        return defaults


def save_categories(categories):
    """Write the categories list to the 'Categories' Google Sheet tab."""
    try:
        spreadsheet = _get_spreadsheet()

        try:
            ws = spreadsheet.worksheet("Categories")
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet("Categories", rows=len(categories) + 1, cols=1)

        ws.clear()
        rows = [["Category"]] + [[c] for c in categories]
        ws.update(rows, value_input_option="USER_ENTERED")
    except Exception as e:
        st.warning(f"⚠️ Could not save categories to Google Sheets: {e}")


def load_category_rules():
    """Load description→category rules from the 'Category Rules' Google Sheet."""
    try:
        spreadsheet = _get_spreadsheet()

        try:
            ws = spreadsheet.worksheet("Category Rules")
        except gspread.exceptions.WorksheetNotFound:
            return {}

        records = ws.get_all_records()
        rules = {}
        for row in records:
            description = str(row.get("Description", "")).strip().lower()
            category = str(row.get("Category", "")).strip()
            if description and category:
                rules[description] = category
        return rules
    except Exception:
        return {}


def save_category_rules(rules):
    """Save description→category rules to the 'Category Rules' Google Sheet."""
    try:
        spreadsheet = _get_spreadsheet()

        try:
            ws = spreadsheet.worksheet("Category Rules")
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet("Category Rules", rows=1, cols=2)

        ws.clear()
        rows = [["Description", "Category"]]
        for description in sorted(rules.keys()):
            rows.append([description, rules[description]])
        ws.update(rows, value_input_option="USER_ENTERED")
    except Exception as e:
        st.warning(f"⚠️ Could not save category rules to Google Sheets: {e}")


def calculate_shared_split(df, partners, has_shared_partner):
    """Calculate per-person breakdown including shared expense splitting.

    Returns a dict with:
        individual_totals: {name: amount} for each real partner's own expenses
        shared_total: total of all Shared expenses
        per_person_share: shared_total / number of real partners
        grand_totals: {name: individual + per_person_share}
        real_partners: list of partner names excluding "Shared"
    """
    real_partners = [p for p in partners if p != "Shared"]

    if not has_shared_partner or "Shared" not in partners:
        # No shared partner — simple totals
        individual_totals = {}
        for p in real_partners:
            individual_totals[p] = df.loc[df['Partner'] == p, 'Amount'].sum()
        return {
            'individual_totals': individual_totals,
            'shared_total': 0.0,
            'per_person_share': 0.0,
            'grand_totals': dict(individual_totals),
            'real_partners': real_partners,
        }

    individual_totals = {}
    for p in real_partners:
        individual_totals[p] = df.loc[df['Partner'] == p, 'Amount'].sum()

    shared_total = df.loc[df['Partner'] == 'Shared', 'Amount'].sum()
    per_person_share = shared_total / len(real_partners) if real_partners else 0.0

    grand_totals = {}
    for p in real_partners:
        grand_totals[p] = individual_totals[p] + per_person_share

    return {
        'individual_totals': individual_totals,
        'shared_total': shared_total,
        'per_person_share': per_person_share,
        'grand_totals': grand_totals,
        'real_partners': real_partners,
    }

def write_to_google_sheets(df, partners, has_shared_partner):
    """Write expense data to an existing Google Sheet and return its URL."""
    spreadsheet = _get_spreadsheet()

    # --- Worksheet 1: All Expenses ---
    export_df = df.drop(columns=["Verified"], errors="ignore").copy()
    if "Date" in export_df.columns:
        export_df["Date"] = export_df["Date"].astype(str)
    export_df = export_df.fillna("")

    try:
        ws1 = spreadsheet.worksheet("All Expenses")
    except gspread.exceptions.WorksheetNotFound:
        ws1 = spreadsheet.add_worksheet("All Expenses", rows=1, cols=1)
    ws1.clear()
    ws1.update(
        [export_df.columns.tolist()] + export_df.values.tolist(),
        value_input_option="USER_ENTERED",
    )

    # --- Worksheet 2: Summary ---
    try:
        ws2 = spreadsheet.worksheet("Summary")
    except gspread.exceptions.WorksheetNotFound:
        ws2 = spreadsheet.add_worksheet("Summary", rows=20, cols=10)
    ws2.clear()

    if has_shared_partner:
        breakdown = calculate_shared_split(df, partners, has_shared_partner)
        rows = [["Partner", "Own Total", "Share of Shared", "Grand Total"]]
        for p in breakdown["real_partners"]:
            rows.append([
                p,
                round(breakdown["individual_totals"][p], 2),
                round(breakdown["per_person_share"], 2),
                round(breakdown["grand_totals"][p], 2),
            ])
        rows.append([
            "Shared Total",
            round(breakdown["shared_total"], 2),
            "",
            "",
        ])
    else:
        rows = [["Partner", "Total"]]
        for p in partners:
            total = df.loc[df["Partner"] == p, "Amount"].sum()
            rows.append([p, round(total, 2)])

    ws2.update(rows, value_input_option="USER_ENTERED")

    return spreadsheet.url


def generate_excel(df, partners=None, has_shared_partner=False):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df = df.drop(columns=['Verified'], errors='ignore')
        export_df.to_excel(writer, index=False, sheet_name='Expenses')

        worksheet = writer.sheets['Expenses']
        for i, col in enumerate(export_df.columns):
            # precise column width for mixed languages
            col_max = export_df[col].astype(str).map(len).max()
            max_len = max(col_max if pd.notna(col_max) else 0, len(col)) + 5
            worksheet.set_column(i, i, max_len)

        # Summary sheet when shared partner is enabled
        if has_shared_partner and partners:
            breakdown = calculate_shared_split(df, partners, has_shared_partner)

            summary_rows = []
            for p in breakdown['real_partners']:
                summary_rows.append({
                    'Partner': p,
                    'Own Total': breakdown['individual_totals'][p],
                    'Share of Shared': breakdown['per_person_share'],
                    'Grand Total': breakdown['grand_totals'][p],
                })
            summary_rows.append({
                'Partner': 'Shared Total',
                'Own Total': breakdown['shared_total'],
                'Share of Shared': '',
                'Grand Total': '',
            })

            summary_df = pd.DataFrame(summary_rows)
            summary_df.to_excel(writer, index=False, sheet_name='Summary')

            ws = writer.sheets['Summary']
            for i, col in enumerate(summary_df.columns):
                col_max = summary_df[col].astype(str).map(len).max()
                max_len = max(col_max if pd.notna(col_max) else 0, len(col)) + 5
                ws.set_column(i, i, max_len)

    return output.getvalue()