import streamlit as st
import pandas as pd
from utils import load_excel, extract_categories

def render_setup_page():
    st.title("🧾 Expense App Setup")
    
    # --- 1. DEFINE PARTNERS (Only if not already set) ---
    if not st.session_state.partners:
        st.subheader("1. Define Partners")
        with st.container(border=True):
            num_partners = st.slider("How many roommates?", min_value=2, max_value=7, value=3)
            
            # Temporary dictionary to hold inputs
            current_partners = {} 
            
            cols = st.columns(3)
            default_colors = ["#FF4B4B", "#1E90FF", "#228B22", "#FFA500", "#9370DB", "#008080", "#FF1493"]
            default_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]

            for i in range(num_partners):
                with cols[i % 3]: 
                    p_name = st.text_input(f"Name {i+1}", value=default_names[i], key=f"p_name_{i}")
                    p_color = st.color_picker(f"Color {i+1}", default_colors[i], key=f"p_col_{i}")
                    current_partners[p_name] = p_color
            
            # Button to save partners so we don't lose them when adding files
            if st.button("Confirm Partners"):
                st.session_state.partners = current_partners
                st.rerun()
    else:
        # If partners are set, show a small summary and a "Edit" button
        st.success(f"✅ **{len(st.session_state.partners)} Partners Configured:** " + ", ".join(st.session_state.partners.keys()))
        if st.button("✏️ Edit Partners"):
            st.session_state.partners = {} # Reset to allow editing
            st.rerun()

    st.divider()

    # --- 2. MULTI-FILE UPLOAD LOOP ---
    st.subheader("2. Upload Expenses")
    st.caption("You can upload multiple Excel files (e.g., Credit Card + Bank Transfers). They will be merged together.")

    # Initialize a key to reset uploader
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    with st.container(border=True):
        # File Uploader with dynamic key to allow resetting
        uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=['xlsx', 'xls'], key=f"uploader_{st.session_state.uploader_key}")
        
        if uploaded_file:
            st.info("Mapping columns for: " + uploaded_file.name)
            try:
                preview_df = pd.read_excel(uploaded_file, nrows=0)
                columns = preview_df.columns.tolist()
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Required**")
                    date_col = st.selectbox("Date", columns, index=0 if len(columns)>0 else 0)
                    desc_col = st.selectbox("Description", columns, index=1 if len(columns)>1 else 0)
                    amt_col = st.selectbox("Amount", columns, index=2 if len(columns)>2 else 0)
                
                with c2:
                    st.markdown("**Optional (Pre-filled)**")
                    opt_cols = ["None"] + columns
                    partner_col = st.selectbox("Partner", opt_cols)
                    cat_col = st.selectbox("Category", opt_cols)
                    comment_col = st.selectbox("Comment", opt_cols)

                st.markdown("---")
                
                # ACTION: ADD FILE
                if st.button("➕ Add This File to Batch", type="primary"):
                    mapping = {
                        'date': date_col, 'desc': desc_col, 'amt': amt_col,
                        'partner': partner_col, 'cat': cat_col, 'comment': comment_col
                    }
                    new_data = load_excel(uploaded_file, mapping)
                    
                    if new_data is not None:
                        # 1. Extract Categories
                        imported_cats = extract_categories(new_data)
                        for cat in imported_cats:
                            if cat not in st.session_state.categories:
                                st.session_state.categories.append(cat)
                        
                        # 2. Append to Session State
                        st.session_state.expenses = pd.concat([st.session_state.expenses, new_data], ignore_index=True)
                        
                        # 3. Reset Uploader for next file
                        st.session_state.uploader_key += 1
                        st.toast(f"✅ Added {len(new_data)} rows! Upload another or Finish.")
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # --- 3. STATUS & FINISH ---
    st.divider()
    
    total_rows = len(st.session_state.expenses)
    if total_rows > 0:
        st.markdown(f"### 📊 Total Expenses Loaded: **{total_rows}**")
        st.dataframe(st.session_state.expenses.tail(3), hide_index=True) # Show last 3 added
        
        if st.button(f"✅ Finish & Go to Dashboard ({total_rows} items)", type="primary", use_container_width=True):
            if not st.session_state.partners:
                st.error("❌ You haven't defined your partners yet! Go back to Step 1 and click 'Confirm Partners'.")
            else:
                st.session_state.setup_complete = True
                st.rerun()