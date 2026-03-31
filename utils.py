import os
import pandas as pd
import io
import streamlit as st

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

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def auto_detect_columns(df, keywords=None):
    """Match DataFrame column headers to known field names via keyword lookup."""
    kw_map = COLUMN_KEYWORDS if keywords is None else keywords
    mapping = {}
    used = set()
    for field, kw_list in kw_map.items():
        for col in df.columns:
            if col in used:
                continue
            col_lower = str(col).strip().lower()
            if any(kw in col_lower for kw in kw_list):
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


def extract_categories(df):
    """Extracts unique categories from the loaded dataframe."""
    if 'Category' in df.columns:
        # Get unique values, drop None/NaN, convert to list
        unique_cats = df['Category'].dropna().unique().tolist()
        # Remove "Uncategorized" if it exists so we don't duplicate it
        return [str(c) for c in unique_cats if str(c) != "Uncategorized"]
    return []


def load_categories():
    """Load categories list from local CSV file."""
    defaults = ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]
    filepath = os.path.join(_DATA_DIR, "categories.csv")
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        categories = [str(row).strip() for row in df["Category"].dropna() if str(row).strip()]
        return categories if categories else defaults
    except Exception:
        return defaults


def save_categories(categories):
    """Write the categories list to local CSV file."""
    filepath = os.path.join(_DATA_DIR, "categories.csv")
    os.makedirs(_DATA_DIR, exist_ok=True)
    df = pd.DataFrame({"Category": categories})
    df.to_csv(filepath, index=False, encoding="utf-8-sig")


def load_category_rules():
    """Load description→category rules from local CSV file."""
    filepath = os.path.join(_DATA_DIR, "category_rules.csv")
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        rules = {}
        for _, row in df.iterrows():
            description = str(row.get("Description", "")).strip().lower()
            category = str(row.get("Category", "")).strip()
            if description and category:
                rules[description] = category
        return rules
    except Exception:
        return {}


def save_category_rules(rules):
    """Save description→category rules to local CSV file."""
    filepath = os.path.join(_DATA_DIR, "category_rules.csv")
    os.makedirs(_DATA_DIR, exist_ok=True)
    rows = [{"Description": k, "Category": v} for k, v in sorted(rules.items())]
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")


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

    return output.getvalue()
