import pandas as pd
import io
import streamlit as st

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
    # Don't overwrite Category yet, we want to save the Hebrew ones
    df['Category'] = df['Category'].fillna("Uncategorized")
    df['Comment'] = df['Comment'].fillna("")

    # --- NEW: VERIFICATION FLAG ---
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


def generate_excel(df, partners=None, has_shared_partner=False):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df = df.drop(columns=['Verified'], errors='ignore')
        export_df.to_excel(writer, index=False, sheet_name='Expenses')

        worksheet = writer.sheets['Expenses']
        for i, col in enumerate(export_df.columns):
            # precise column width for mixed languages
            max_len = max(export_df[col].astype(str).map(len).max(), len(col)) + 5
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
                max_len = max(summary_df[col].astype(str).map(len).max(), len(col)) + 5
                ws.set_column(i, i, max_len)

    return output.getvalue()