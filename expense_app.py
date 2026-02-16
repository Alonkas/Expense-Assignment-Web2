import streamlit as st
import pandas as pd
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Roommate Expense Manager", layout="wide", page_icon="🧾")

# --- STATE INITIALIZATION ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame()
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
if 'partners' not in st.session_state:
    st.session_state.partners = {}
if 'categories' not in st.session_state:
    st.session_state.categories = ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]

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
    expected_cols = ['Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment']
    df = df[[col for col in expected_cols if col in df.columns]]
    
    # Add missing standard columns
    for col in expected_cols:
        if col not in df.columns:
            if col == 'Amount': df[col] = 0.0
            elif col == 'Category': df[col] = "Uncategorized"
            elif col == 'Comment': df[col] = ""
            else: df[col] = None

    # --- DATE FIX: Force Day-First Parsing ---
    try:
        # dayfirst=True handles dd/mm/yyyy correctly
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        
        # Check for bad dates
        invalid_dates = df['Date'].isna().sum()
        if invalid_dates > 0:
            st.warning(f"⚠️ {invalid_dates} rows had invalid dates and were skipped.")
            df = df.dropna(subset=['Date'])
            
    except Exception as e:
        st.error(f"Date parsing error: {e}")
        return None
    
    return df

def generate_excel(df):
    """Generates an Excel file in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses')
        worksheet = writer.sheets['Expenses']
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    return output.getvalue()

# ==========================================
# PHASE 1: INITIALIZED SETUP PAGE
# ==========================================
if not st.session_state.setup_complete:
    st.title("🧾 Expense App Setup")
    st.markdown("Welcome! Let's set up your roommates and upload your first bill.")
    
    with st.container(border=True):
        st.subheader("1. Define Partners")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            p1 = st.text_input("Partner 1 Name", value="Alice")
            col1 = st.color_picker("Color 1", "#FF4B4B")
        with c2:
            p2 = st.text_input("Partner 2 Name", value="Bob")
            col2 = st.color_picker("Color 2", "#1E90FF")
        with c3:
            p3 = st.text_input("Partner 3 Name", value="Charlie")
            col3 = st.color_picker("Color 3", "#228B22")
            
    with st.container(border=True):
        st.subheader("2. Upload & Map Excel")
        uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=['xlsx', 'xls'])
        
        if uploaded_file:
            st.info("File uploaded! Now map the columns below so we understand your data.")
            preview_df = pd.read_excel(uploaded_file, nrows=0)
            columns = preview_df.columns.tolist()
            
            c_map1, c_map2 = st.columns(2)
            
            with c_map1:
                st.markdown("**Required Columns**")
                date_col = st.selectbox("Date Column", columns, index=0 if len(columns)>0 else 0)
                desc_col = st.selectbox("Description Column", columns, index=1 if len(columns)>1 else 0)
                amt_col = st.selectbox("Amount Column", columns, index=2 if len(columns)>2 else 0)
            
            with c_map2:
                st.markdown("**Optional Columns** (Select 'None' if missing)")
                opt_cols = ["None"] + columns
                partner_col = st.selectbox("Partner Column", opt_cols)
                cat_col = st.selectbox("Category Column", opt_cols)
                comment_col = st.selectbox("Comment Column", opt_cols)

            st.markdown("---")
            
            if st.button("🚀 Start Expense Assignment", type="primary", use_container_width=True):
                # Save Partners
                st.session_state.partners = {p1: col1, p2: col2, p3: col3}
                
                # Process File
                mapping = {
                    'date': date_col, 'desc': desc_col, 'amt': amt_col,
                    'partner': partner_col, 'cat': cat_col, 'comment': comment_col
                }
                new_data = load_excel(uploaded_file, mapping)
                
                if new_data is not None:
                    st.session_state.expenses = new_data
                    st.session_state.setup_complete = True
                    st.rerun()

# ==========================================
# PHASE 2 & 3: MAIN APPLICATION (After Setup)
# ==========================================
else:
    # Sidebar for persistent info
    with st.sidebar:
        st.header("Roommates")
        for p, c in st.session_state.partners.items():
            st.markdown(f"**<span style='color:{c}'>●</span> {p}**", unsafe_allow_html=True)
        
        st.divider()
        if st.button("🔄 Reset / New Setup"):
            st.session_state.setup_complete = False
            st.session_state.expenses = pd.DataFrame()
            st.rerun()

    st.title("💰 Expense Dashboard")

    # Tabs
    tab_focus, tab_table, tab_results = st.tabs(["🎯 Focus Mode", "📊 Table View", "🏁 Final Results"])

    # --- FOCUS MODE ---
    with tab_focus:
        df = st.session_state.expenses
        unassigned = df[df['Partner'].isna() | (df['Partner'] == "")].index.tolist()
        
        if not unassigned:
            st.success("🎉 All expenses assigned!")
        else:
            curr_idx = unassigned[0]
            row = df.loc[curr_idx]
            
            # Progress
            st.progress(int((len(df) - len(unassigned)) / len(df) * 100), 
                       f"Remaining: {len(unassigned)}")

            # Expense Card
            st.markdown(f"""
            <div style="padding:20px; border-radius:10px; background:#f9f9f9; border:1px solid #ddd;">
                <h2 style="margin:0;">${row['Amount']:.2f}</h2>
                <p style="color:gray;">{row['Date']}</p>
                <h3 style="margin-top:5px;">{row['Description']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") # Spacer

            # Inputs
            c_cat, c_com = st.columns(2)
            with c_cat:
                new_cat = st.selectbox("Category", st.session_state.categories, key=f"cat_{curr_idx}")
            with c_com:
                new_com = st.text_input("Comment", value=str(row['Comment']), key=f"com_{curr_idx}")

            # Assign Buttons
            st.write("### Assign to:")
            cols = st.columns(3)
            for i, (name, color) in enumerate(st.session_state.partners.items()):
                with cols[i]:
                    if st.button(f"👤 {name}", key=f"btn_{name}_{curr_idx}", use_container_width=True):
                        st.session_state.expenses.at[curr_idx, 'Partner'] = name
                        st.session_state.expenses.at[curr_idx, 'Category'] = new_cat
                        st.session_state.expenses.at[curr_idx, 'Comment'] = new_com
                        st.rerun()

    # --- TABLE VIEW ---
    with tab_table:
        edited = st.data_editor(
            st.session_state.expenses,
            column_config={
                "Partner": st.column_config.SelectboxColumn(options=list(st.session_state.partners.keys()), required=True),
                "Category": st.column_config.SelectboxColumn(options=st.session_state.categories, required=True)
            },
            use_container_width=True,
            num_rows="dynamic"
        )
        if not edited.equals(st.session_state.expenses):
            st.session_state.expenses = edited
            st.rerun()

    # --- RESULTS ---
    with tab_results:
        st.subheader("Final Split")
        res_df = st.session_state.expenses
        if not res_df.empty:
            totals = res_df.groupby("Partner")['Amount'].sum()
            c_res = st.columns(3)
            for i, (p, c) in enumerate(st.session_state.partners.items()):
                with c_res[i]:
                    st.metric(label=p, value=f"${totals.get(p, 0):,.2f}")
            
            st.download_button("Download Report", data=generate_excel(res_df), file_name="Report.xlsx")