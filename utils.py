import pandas as pd
import io
import csv
import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

LOCAL_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

COLUMN_KEYWORDS = {
    'date': ['date', 'תאריך', 'תאריך עסקה'],
    'desc': ['description', 'desc', 'תיאור', 'פירוט', 'שם בית העסק'],
    'amt': ['amount', 'sum', 'סכום', 'סכום חיוב'],
    'source': ['source', 'credit card', 'כרטיס', 'מקור'],
    'partner': ['partner', 'roommate', 'שותף', 'שם'],
    'cat': ['category', 'cat', 'קטגוריה'],
    'comment': ['comment', 'note', 'notes', 'הערה', 'הערות'],
}
SHARED_KEYWORDS = ['shared', 'משותף', 'common']


def auto_detect_columns(df):
    """Match DataFrame column headers to known field names via keyword lookup."""
    mapping = {}
    used = set()
    for field, keywords in COLUMN_KEYWORDS.items():
        for col in df.columns:
            if col in used:
                continue
            col_lower = str(col).strip().lower()
            if any(kw in col_lower for kw in keywords):
                mapping[field] = col
                used.add(col)
                break
    # Required fields → None if unmatched; optional → "None" string
    for field in ['date', 'desc', 'amt']:
        mapping.setdefault(field, None)
    for field in ['source', 'partner', 'cat', 'comment']:
        mapping.setdefault(field, "None")
    return mapping


def apply_mapping(df, mapping):
    """Apply column mapping, rename, normalize, and clean a DataFrame."""
    rename_dict = {
        mapping['date']: 'Date',
        mapping['desc']: 'Description',
        mapping['amt']: 'Amount'
    }

    if mapping.get('source') and mapping['source'] != "None":
        rename_dict[mapping['source']] = 'Source'
    if mapping.get('partner') and mapping['partner'] != "None":
        rename_dict[mapping['partner']] = 'Partner'
    if mapping.get('cat') and mapping['cat'] != "None":
        rename_dict[mapping['cat']] = 'Category'
    if mapping.get('comment') and mapping['comment'] != "None":
        rename_dict[mapping['comment']] = 'Comment'

    df = df.rename(columns=rename_dict)

    # Normalize Columns
    expected_cols = ['Source', 'Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    df = df[expected_cols]

    # --- CLEANING DATA ---
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0.0)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
    df = df.dropna(subset=['Date'])

    df['Source'] = df['Source'].fillna("")
    df['Partner'] = df['Partner'].replace(["", " ", "nan"], None)
    df['Category'] = df['Category'].fillna("Uncategorized")
    df['Comment'] = df['Comment'].fillna("")

    df['Verified'] = False

    return df


def load_excel(file, mapping):
    try:
        df = pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

    return apply_mapping(df, mapping)

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
    """Load categories list from local CSV file."""
    defaults = ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]
    filepath = os.path.join(LOCAL_DATA_DIR, "categories.csv")
    if not os.path.exists(filepath):
        return defaults
    try:
        with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            categories = [row["Category"].strip() for row in reader if row.get("Category", "").strip()]
        return categories if categories else defaults
    except Exception as e:
        st.warning(f"Could not load categories from {filepath}: {e}")
        return defaults


def save_categories(categories):
    """Write the categories list to local CSV file."""
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    filepath = os.path.join(LOCAL_DATA_DIR, "categories.csv")
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Category"])
            for c in categories:
                writer.writerow([c])
    except Exception as e:
        st.warning(f"Could not save categories to {filepath}: {e}")


def load_category_rules():
    """Load description-to-category rules from local CSV file."""
    filepath = os.path.join(LOCAL_DATA_DIR, "category_rules.csv")
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rules = {}
            for row in reader:
                description = row.get("Description", "").strip().lower()
                category = row.get("Category", "").strip()
                if description and category:
                    rules[description] = category
        return rules
    except Exception:
        return {}


def save_category_rules(rules):
    """Save description-to-category rules to local CSV file."""
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    filepath = os.path.join(LOCAL_DATA_DIR, "category_rules.csv")
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Description", "Category"])
            for description in sorted(rules.keys()):
                writer.writerow([description, rules[description]])
    except Exception as e:
        st.warning(f"Could not save category rules to {filepath}: {e}")


def calculate_shared_split(df, partners, has_shared_partner, shares_shared=None):
    """Calculate per-person breakdown including shared expense splitting.

    Returns a dict with:
        individual_totals: {name: amount} for each real partner's own expenses
        shared_total: total of all Shared expenses
        per_person_share: shared_total / number of sharing partners
        grand_totals: {name: individual + per_person_share (if sharing)}
        real_partners: list of partner names excluding "Shared"
        sharing_partners: list of partners who participate in shared split
    """
    if shares_shared is None:
        shares_shared = {}
    real_partners = [p for p in partners if p != "Shared"]
    sharing_partners = [p for p in real_partners if shares_shared.get(p, True)]

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
            'sharing_partners': sharing_partners,
        }

    individual_totals = {}
    for p in real_partners:
        individual_totals[p] = df.loc[df['Partner'] == p, 'Amount'].sum()

    shared_total = df.loc[df['Partner'] == 'Shared', 'Amount'].sum()
    per_person_share = shared_total / len(sharing_partners) if sharing_partners else 0.0

    grand_totals = {}
    for p in real_partners:
        if p in sharing_partners:
            grand_totals[p] = individual_totals[p] + per_person_share
        else:
            grand_totals[p] = individual_totals[p]

    return {
        'individual_totals': individual_totals,
        'shared_total': shared_total,
        'per_person_share': per_person_share,
        'grand_totals': grand_totals,
        'real_partners': real_partners,
        'sharing_partners': sharing_partners,
    }

def write_to_google_sheets(df, partners, has_shared_partner, shares_shared=None):
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
    all_data = [export_df.columns.tolist()] + export_df.values.tolist()
    ws1.resize(len(all_data), len(export_df.columns))
    ws1.update(all_data, value_input_option="USER_ENTERED")

    # --- Worksheet 2: Summary ---
    try:
        ws2 = spreadsheet.worksheet("Summary")
    except gspread.exceptions.WorksheetNotFound:
        ws2 = spreadsheet.add_worksheet("Summary", rows=20, cols=10)
    ws2.clear()

    if has_shared_partner:
        breakdown = calculate_shared_split(df, partners, has_shared_partner, shares_shared)
        rows = [["Partner", "Own Total", "Share of Shared", "Grand Total"]]
        for p in breakdown["real_partners"]:
            share_val = breakdown["per_person_share"] if p in breakdown["sharing_partners"] else 0.0
            rows.append([
                p,
                round(breakdown["individual_totals"][p], 2),
                round(share_val, 2),
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

    ws2.resize(len(rows), len(rows[0]))
    ws2.update(rows, value_input_option="USER_ENTERED")

    # --- Per-partner worksheets ---
    if partners:
        amount_col = export_df.columns.tolist().index("Amount") if "Amount" in export_df.columns else None
        for name in partners:
            partner_df = export_df[export_df["Partner"] == name].reset_index(drop=True)
            sheet_name = name[:100]  # Google Sheets allows up to 100 chars
            try:
                ws_p = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                ws_p = spreadsheet.add_worksheet(sheet_name, rows=1, cols=1)
            ws_p.clear()

            data_rows = [partner_df.columns.tolist()] + partner_df.values.tolist()
            # Add bold Total row
            total_row = [""] * len(partner_df.columns)
            total_row[0] = "Total"
            if amount_col is not None and len(partner_df) > 0:
                total_row[amount_col] = round(partner_df["Amount"].sum(), 2)
            data_rows.append(total_row)

            # Resize to fit data + category summary section
            num_categories = partner_df["Category"].nunique() if len(partner_df) > 0 else 0
            # rows: header + data + total + separator + cat title + cat headers + categories + cat total
            total_rows = len(data_rows) + (4 + num_categories if num_categories > 0 else 0)
            total_cols = max(len(partner_df.columns), 3)  # at least 3 for category summary
            ws_p.resize(total_rows, total_cols)

            ws_p.update(data_rows, value_input_option="USER_ENTERED")

            # Bold the Total row
            total_row_idx = len(partner_df) + 2  # +1 header, +1 for 1-based indexing
            ws_p.format(
                f"A{total_row_idx}:{chr(65 + len(partner_df.columns) - 1)}{total_row_idx}",
                {"textFormat": {"bold": True}},
            )

            # Category Summary breakdown
            if len(partner_df) > 0:
                cat_sums = (
                    partner_df.groupby("Category")["Amount"]
                    .sum()
                    .sort_values(ascending=False)
                )
                cat_total = cat_sums.sum()

                cat_rows = [
                    [""],  # blank separator
                    ["Category Summary", "", ""],
                    ["Category", "Amount", "% of Total"],
                ]
                for cat, amt in cat_sums.items():
                    pct = f"{amt / cat_total * 100:.1f}%" if cat_total else "0.0%"
                    cat_rows.append([cat, round(float(amt), 2), pct])
                cat_rows.append(["Total", round(float(cat_total), 2), "100.0%"])

                cat_start_row = total_row_idx + 1  # row after Total
                ws_p.update(
                    f"A{cat_start_row}",
                    cat_rows,
                    value_input_option="USER_ENTERED",
                )

                # Bold header and total rows
                header_row = cat_start_row + 1  # "Category Summary" title
                col_header_row = cat_start_row + 2  # Column headers
                cat_total_row = cat_start_row + 2 + len(cat_sums) + 1  # Total row
                ws_p.format(f"A{header_row}:C{header_row}", {"textFormat": {"bold": True}})
                ws_p.format(f"A{col_header_row}:C{col_header_row}", {"textFormat": {"bold": True}})
                ws_p.format(f"A{cat_total_row}:C{cat_total_row}", {"textFormat": {"bold": True}})

    return spreadsheet.url


def generate_excel(df, partners=None, has_shared_partner=False, shares_shared=None):
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
            breakdown = calculate_shared_split(df, partners, has_shared_partner, shares_shared)

            summary_rows = []
            for p in breakdown['real_partners']:
                share_val = breakdown['per_person_share'] if p in breakdown['sharing_partners'] else 0.0
                summary_rows.append({
                    'Partner': p,
                    'Own Total': breakdown['individual_totals'][p],
                    'Share of Shared': share_val,
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

        # Per-partner sheets
        if partners:
            bold = writer.book.add_format({'bold': True})
            pct_fmt = writer.book.add_format({'num_format': '0.0%'})
            pct_bold_fmt = writer.book.add_format({'num_format': '0.0%', 'bold': True})
            amount_col_idx = list(export_df.columns).index('Amount') if 'Amount' in export_df.columns else None

            for name in partners:
                partner_df = export_df[export_df['Partner'] == name].reset_index(drop=True)
                sheet_name = name[:31]  # xlsxwriter 31-char limit
                partner_df.to_excel(writer, index=False, sheet_name=sheet_name)

                ws_p = writer.sheets[sheet_name]
                # Auto-size columns
                for i, col in enumerate(partner_df.columns):
                    col_max = partner_df[col].astype(str).map(len).max()
                    max_len = max(col_max if pd.notna(col_max) else 0, len(col)) + 5
                    ws_p.set_column(i, i, max_len)

                # Total row
                total_row = len(partner_df) + 1  # +1 for header
                ws_p.write(total_row, 0, 'Total', bold)
                if amount_col_idx is not None and len(partner_df) > 0:
                    ws_p.write_formula(
                        total_row, amount_col_idx,
                        f'=SUM({chr(65 + amount_col_idx)}2:{chr(65 + amount_col_idx)}{total_row})',
                        bold
                    )

                # Category Summary breakdown
                if len(partner_df) > 0:
                    cat_sums = (
                        partner_df.groupby('Category')['Amount']
                        .sum()
                        .sort_values(ascending=False)
                    )
                    cat_total = cat_sums.sum()

                    cat_start_row = total_row + 2  # blank row separator
                    ws_p.write(cat_start_row, 0, 'Category Summary', bold)
                    ws_p.write(cat_start_row + 1, 0, 'Category', bold)
                    ws_p.write(cat_start_row + 1, 1, 'Amount', bold)
                    ws_p.write(cat_start_row + 1, 2, '% of Total', bold)

                    for ci, (cat, amt) in enumerate(cat_sums.items()):
                        r = cat_start_row + 2 + ci
                        ws_p.write(r, 0, cat)
                        ws_p.write(r, 1, round(amt, 2))
                        ws_p.write(r, 2, amt / cat_total if cat_total else 0, pct_fmt)

                    cat_total_row = cat_start_row + 2 + len(cat_sums)
                    ws_p.write(cat_total_row, 0, 'Total', bold)
                    ws_p.write(cat_total_row, 1, round(cat_total, 2), bold)
                    ws_p.write(cat_total_row, 2, 1.0, pct_bold_fmt)

    return output.getvalue()