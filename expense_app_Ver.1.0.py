import streamlit as st
import pandas as pd
import io

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="Roommate Expense Manager", layout="wide", page_icon="🧾")

# Initialize Session State
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame()
if 'categories' not in st.session_state:
    st.session_state.categories = ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'partners' not in st.session_state:
    st.session_state.partners = {}

# --- HELPER FUNCTIONS ---
def load_excel(file, mapping):
    """Loads and normalizes the uploaded Excel file based on user mapping."""
    try:
        df = pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

    # Rename columns based on mapping
    rename_dict = {
        mapping['date']: 'Date',
        mapping['desc']: 'Description',
        mapping['amt']: 'Amount'
    }
    
    # Handle Optional Columns
    if mapping.get('partner') and mapping['partner'] != "None":
        rename_dict[mapping['partner']] = 'Partner'
    
    if mapping.get('cat') and mapping['cat'] != "None":
        rename_dict[mapping['cat']] = 'Category'
    
    if mapping.get('comment') and mapping['comment'] != "None":
        rename_dict[mapping['comment']] = 'Comment'

    df = df.rename(columns=rename_dict)
    
    # Normalize Data
    df = df[[col for col in ['Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment'] if col in df.columns]]
    
    # Add missing standard columns if they don't exist
    if 'Partner' not in df.columns:
        df['Partner'] = None
    if 'Category' not in df.columns:
        df['Category'] = "Uncategorized"
    if 'Comment' not in df.columns:
        df['Comment'] = ""

    # --- FIX: FORCE DAY-FIRST PARSING ---
    try:
        # dayfirst=True fixes the dd/mm/yyyy issue
        # errors='coerce' turns bad dates into NaT (Not a Time) instead of crashing
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        
        # Drop rows where date failed to parse (optional, keeps data clean)
        if df['Date'].isna().any():
            st.warning(f"⚠️ {df['Date'].isna().sum()} rows had invalid dates and were skipped.")
            df = df.dropna(subset=['Date'])
            
    except Exception as e:
        st.error(f"Date parsing error: {e}")
        return None
    
    return df

    # Rename columns based on mapping
    rename_dict = {
        mapping['date']: 'Date',
        mapping['desc']: 'Description',
        mapping['amt']: 'Amount'
    }
    
    # Handle Optional Columns
    if mapping.get('partner') and mapping['partner'] != "None":
        rename_dict[mapping['partner']] = 'Partner'
    
    if mapping.get('cat') and mapping['cat'] != "None":
        rename_dict[mapping['cat']] = 'Category'
    
    if mapping.get('comment') and mapping['comment'] != "None":
        rename_dict[mapping['comment']] = 'Comment'

    df = df.rename(columns=rename_dict)
    
    # Normalize Data
    df = df[[col for col in ['Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment'] if col in df.columns]]
    
    # Add missing standard columns if they don't exist
    if 'Partner' not in df.columns:
        df['Partner'] = None
    if 'Category' not in df.columns:
        df['Category'] = "Uncategorized"
    if 'Comment' not in df.columns:
        df['Comment'] = ""

    # Ensure Date is formatted nicely
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    return df

def generate_excel(df):
    """Generates an Excel file in memory for download."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses')
        # Auto-adjust column width
        worksheet = writer.sheets['Expenses']
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    return output.getvalue()

# --- SIDEBAR: PHASE 1 (SETUP) ---
with st.sidebar:
    st.header("Phase 1: Setup")
    
    with st.expander("3.1 Partner Setup", expanded=True):
        p1 = st.text_input("Partner 1 Name", value="Alice")
        c1 = st.color_picker("P1 Color", "#FF4B4B")
        
        p2 = st.text_input("Partner 2 Name", value="Bob")
        c2 = st.color_picker("P2 Color", "#1E90FF")
        
        p3 = st.text_input("Partner 3 Name", value="Charlie")
        c3 = st.color_picker("P3 Color", "#228B22")
        
        # Update session state
        st.session_state.partners = {p1: c1, p2: c2, p3: c3}

    st.divider()

    with st.expander("3.2 Upload & Mapping", expanded=not st.session_state.expenses.empty):
        uploaded_file = st.file_uploader("Upload Excel Expense File", type=['xlsx', 'xls'])
        
        if uploaded_file:
            # Read just columns for mapping
            preview_df = pd.read_excel(uploaded_file, nrows=0)
            columns = preview_df.columns.tolist()
            
            st.caption("Map your Excel columns:")
            date_col = st.selectbox("Date Column", columns, index=0 if len(columns)>0 else 0)
            desc_col = st.selectbox("Description Column", columns, index=1 if len(columns)>1 else 0)
            amt_col = st.selectbox("Amount Column", columns, index=2 if len(columns)>2 else 0)
            
            st.caption("Optional (Select 'None' if missing):")
            opt_cols = ["None"] + columns
            partner_col = st.selectbox("Partner Column (Pre-filled)", opt_cols)
            cat_col = st.selectbox("Category Column", opt_cols)
            comment_col = st.selectbox("Comment Column", opt_cols)
            
            if st.button("Process & Add File"):
                mapping = {
                    'date': date_col, 'desc': desc_col, 'amt': amt_col,
                    'partner': partner_col, 'cat': cat_col, 'comment': comment_col
                }
                new_data = load_excel(uploaded_file, mapping)
                
                if new_data is not None:
                    # Merge logic (Phase 4)
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)
                    st.success(f"Added {len(new_data)} rows!")
                    st.rerun()

    if st.button("Clear All Data"):
        st.session_state.expenses = pd.DataFrame()
        st.session_state.current_index = 0
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🧾 Expense Manager")

# Check if data exists
if st.session_state.expenses.empty:
    st.info("👈 Please setup partners and upload an Excel file in the sidebar to begin.")
    st.stop()

# --- TABS FOR DIFFERENT MODES ---
tab_focus, tab_table, tab_results = st.tabs(["🎯 Focus Mode (Assignment)", "📊 Table View (Edit)", "🏁 Final Results"])

# === PHASE 3A: FOCUS MODE ===
with tab_focus:
    # Filter unassigned expenses
    # We consider "unassigned" if Partner is None or NaN
    df = st.session_state.expenses
    unassigned_mask = df['Partner'].isna() | (df['Partner'] == "")
    unassigned_indices = df[unassigned_mask].index.tolist()
    
    total_unassigned = len(unassigned_indices)
    
    if total_unassigned == 0:
        st.balloons()
        st.success("🎉 All expenses have been assigned! Check the Results tab.")
    else:
        # Progress Bar
        total_rows = len(df)
        progress = int(((total_rows - total_unassigned) / total_rows) * 100)
        st.progress(progress, text=f"Progress: {total_rows - total_unassigned} of {total_rows} assigned")

        # Get current row to edit
        # We always take the first available unassigned index
        current_idx = unassigned_indices[0]
        row = df.loc[current_idx]

        st.markdown("---")
        
        # Display Large Details
        c_date, c_desc, c_amt = st.columns([1, 3, 2])
        with c_date:
            st.caption("Date")
            st.markdown(f"**{row['Date']}**")
        with c_desc:
            st.caption("Description")
            st.markdown(f"### {row['Description']}")
        with c_amt:
            st.caption("Amount")
            st.markdown(f"# ${row['Amount']:.2f}")

        st.markdown("---")

        # Input Forms
        col_cat, col_comment = st.columns(2)
        with col_cat:
            # Category Handling
            current_cat = row['Category'] if row['Category'] in st.session_state.categories else "Uncategorized"
            selected_cat = st.selectbox(
                "Category", 
                st.session_state.categories + ["+ Add New..."], 
                index=st.session_state.categories.index(current_cat) if current_cat in st.session_state.categories else 0,
                key=f"cat_{current_idx}"
            )
            
            if selected_cat == "+ Add New...":
                new_cat_name = st.text_input("New Category Name")
                if new_cat_name and st.button("Add Category"):
                    st.session_state.categories.append(new_cat_name)
                    st.rerun()
            
        with col_comment:
            comment_input = st.text_input("Comment", value=str(row['Comment']), key=f"comm_{current_idx}")

        # Partner Assignment Buttons (Big & Colored)
        st.write("### Assign to:")
        cols = st.columns(3)
        partners = list(st.session_state.partners.items())

        def assign_partner(idx, partner_name, category, comment):
            st.session_state.expenses.at[idx, 'Partner'] = partner_name
            st.session_state.expenses.at[idx, 'Category'] = category if category != "+ Add New..." else "Uncategorized"
            st.session_state.expenses.at[idx, 'Comment'] = comment
            # No rerun needed strictly if we use logic correctly, but helps refresh UI
            
        for i, (name, color) in enumerate(partners):
            with cols[i]:
                # Styling button with custom CSS logic isn't native, but we use the color in the sidebar
                # Here we just use standard buttons, but bold the text
                if st.button(f"👤 {name}", key=f"btn_{name}_{current_idx}", use_container_width=True):
                    assign_partner(current_idx, name, selected_cat, comment_input)
                    st.rerun()

        # Sidebar Live Totals
        with st.sidebar:
            st.markdown("### 💰 Live Totals")
            live_totals = df.groupby("Partner")['Amount'].sum()
            for name, color in partners:
                amount = live_totals.get(name, 0.0)
                st.markdown(f"<div style='padding:10px; border-radius:5px; border-left: 5px solid {color}; background-color: #f0f2f6; margin-bottom:5px;'>"
                            f"<strong>{name}</strong><br><span style='font-size:1.2em'>${amount:,.2f}</span></div>", 
                            unsafe_allow_html=True)


# === PHASE 3B: TABLE VIEW ===
with tab_table:
    st.subheader("Advanced Editing")
    st.info("💡 You can edit cells directly here. Changes update automatically.")
    
    # Configure Data Editor
    edited_df = st.data_editor(
        st.session_state.expenses,
        column_config={
            "Partner": st.column_config.SelectboxColumn(
                "Partner",
                help="Who paid?",
                width="medium",
                options=list(st.session_state.partners.keys()),
                required=True,
            ),
            "Category": st.column_config.SelectboxColumn(
                "Category",
                width="medium",
                options=st.session_state.categories,
                required=True,
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format="$%.2f",
            ),
        },
        num_rows="dynamic",
        use_container_width=True
    )
    
    # Save manual edits back to session state
    if not edited_df.equals(st.session_state.expenses):
        st.session_state.expenses = edited_df
        st.rerun()

# === PHASE 5: FINAL RESULTS ===
with tab_results:
    st.header("Results Overview")
    
    if st.session_state.expenses.empty:
        st.write("No data yet.")
    else:
        df_res = st.session_state.expenses
        
        # 1. High-Level Summary
        st.subheader("Totals by Partner")
        cols = st.columns(3)
        totals = df_res.groupby("Partner")['Amount'].sum()
        
        for i, (name, color) in enumerate(st.session_state.partners.items()):
            with cols[i]:
                amt = totals.get(name, 0.0)
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 20px; border: 2px solid {color}; border-radius: 10px;">
                        <h3 style="color:{color}">{name}</h3>
                        <h1>${amt:,.2f}</h1>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        st.divider()
        
        # 2. Category Breakdown
        st.subheader("Category Breakdown")
        
        # Pivot table for chart
        pivot_df = df_res.pivot_table(index="Category", columns="Partner", values="Amount", aggfunc="sum", fill_value=0)
        st.bar_chart(pivot_df)

        # 3. Exports
        st.subheader("📤 Export Reports")
        
        c1, c2 = st.columns(2)
        with c1:
            # Combined Export
            excel_data = generate_excel(df_res)
            st.download_button(
                label="Download Combined Report (.xlsx)",
                data=excel_data,
                file_name="roommate_expenses_full.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with c2:
            st.write("Download Individual Reports:")
            for name in st.session_state.partners.keys():
                partner_df = df_res[df_res['Partner'] == name]
                if not partner_df.empty:
                    p_excel = generate_excel(partner_df)
                    st.download_button(
                        label=f"Download {name}'s Report",
                        data=p_excel,
                        file_name=f"expenses_{name}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )