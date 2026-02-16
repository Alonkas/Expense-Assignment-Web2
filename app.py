import streamlit as st
import pandas as pd
from utils import generate_excel
from setup_page import render_setup_page

# --- CONFIGURATION ---
st.set_page_config(page_title="Roommate Expense Manager", layout="wide", page_icon="🧾")

# --- INITIALIZE STATE ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame()
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
if 'partners' not in st.session_state:
    st.session_state.partners = {} # Empty dict
if 'categories' not in st.session_state:
    st.session_state.categories = ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]

# ==========================================
# FLOW CONTROL
# ==========================================

if not st.session_state.setup_complete:
    render_setup_page()
else:
    # --- SIDEBAR: LIVE TOTALS & ACTIONS ---
    with st.sidebar:
        st.header("Actions")
        # BUTTON TO ADD MORE FILES WITHOUT LOSING DATA
        if st.button("📂 Add More Files"):
            st.session_state.setup_complete = False
            st.rerun()
            
        st.divider()
        st.header("💰 Live Totals")
        
        current_totals = st.session_state.expenses.groupby("Partner")['Amount'].sum()
        
        for p, color in st.session_state.partners.items():
            amount = current_totals.get(p, 0.0)
            st.markdown(
                f"""
                <div style="padding:10px; margin-bottom:8px; background-color:white; 
                    border-left: 6px solid {color}; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-weight:bold; font-size:0.9em; color:#555;">{p}</div>
                    <div style="font-size:1.2em; font-weight:bold;">${amount:,.2f}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        st.divider()
        if st.button("🗑️ Reset All Data"):
            st.session_state.setup_complete = False
            st.session_state.expenses = pd.DataFrame()
            st.session_state.partners = {}
            st.rerun()

    st.title("Expense Dashboard")

    # The rest of your app.py remains exactly the same as before...
    # (Copy the tabs logic: Focus Mode, Table View, Results from previous version)
    # ...
    
    tab_focus, tab_table, tab_results = st.tabs(["🎯 Focus Mode (Verification)", "📊 Table View", "🏁 Final Results"])

    # --- TAB 1: FOCUS MODE ---
    with tab_focus:
        df = st.session_state.expenses
        
        # LOGIC CHANGE: Filter by 'Verified' is False
        if 'Verified' not in df.columns:
            df['Verified'] = False # Safety fallback
            
        unverified_indices = df[df['Verified'] == False].index.tolist()
        
        if not unverified_indices:
            st.balloons()
            st.success("🎉 All expenses verified and assigned! Go to 'Final Results'.")
        else:
            # Get current item
            curr_idx = unverified_indices[0]
            row = df.loc[curr_idx]
            
            # Progress Bar
            total_count = len(df)
            done_count = total_count - len(unverified_indices)
            st.progress(done_count / total_count, f"Reviewed: {done_count} / {total_count}")

            # --- EXPENSE CARD ---
            st.markdown(f"""
            <div style="text-align:center; padding:30px; border-radius:15px; background:white; 
                border:1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="color:#888; font-size:1.1em; margin-bottom:5px;">{row['Date']}</div>
                <div style="font-size:1.8em; font-weight:bold; margin-bottom:10px;">{row['Description']}</div>
                <div style="font-size:2.5em; font-weight:900; color:#333;">${row['Amount']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Suggestion Alert
            pre_filled_partner = row['Partner']
            if pre_filled_partner and pre_filled_partner in st.session_state.partners:
                st.info(f"💡 Excel suggests this belongs to **{pre_filled_partner}**. Click their name to confirm.")

            st.write("") 

            # --- INPUTS ---
            c1, c2 = st.columns([1, 1])
            with c1:
                # Category Handling
                current_cat = row['Category'] if row['Category'] in st.session_state.categories else "Uncategorized"
                
                cat_options = st.session_state.categories + ["➕ Add New..."]
                selected_cat = st.selectbox("Category", cat_options, 
                                          index=st.session_state.categories.index(current_cat) if current_cat in st.session_state.categories else 0,
                                          key=f"cat_{curr_idx}")
                
                final_cat = selected_cat
                if selected_cat == "➕ Add New...":
                    new_cat_name = st.text_input("New Category Name", key=f"new_{curr_idx}")
                    if st.button("Save Cat"):
                        st.session_state.categories.append(new_cat_name)
                        st.rerun()
                    final_cat = new_cat_name

            with c2:
                comment = st.text_input("Comment", value=str(row['Comment']), key=f"com_{curr_idx}")

            # --- DYNAMIC PARTNER BUTTONS ---
            st.write("### Assign & Verify:")
            
            partners = list(st.session_state.partners.items())
            num_p = len(partners)

            if num_p > 0:
                # SAFEGUARD: Ensure we request at least 1 column, max 4
                num_cols = min(num_p, 4)
                cols = st.columns(num_cols) 
                
                for i, (name, color) in enumerate(partners):
                    col_idx = i % num_cols  # Wrap buttons if we have more partners than columns
                    with cols[col_idx]:
                        # Highlight button if it matches the pre-filled partner
                        label = f"✅ Confirm {name}" if name == pre_filled_partner else f"👤 {name}"
                        type_btn = "primary" if name == pre_filled_partner else "secondary"
                        
                        if st.button(label, key=f"btn_{name}_{curr_idx}", type=type_btn, use_container_width=True):
                            st.session_state.expenses.at[curr_idx, 'Partner'] = name
                            st.session_state.expenses.at[curr_idx, 'Category'] = final_cat if final_cat != "➕ Add New..." else "Uncategorized"
                            st.session_state.expenses.at[curr_idx, 'Comment'] = comment
                            st.session_state.expenses.at[curr_idx, 'Verified'] = True 
                            st.rerun()
            else:
                st.error("⚠️ No partners found! Please click 'Reset All Data' in the sidebar to setup partners.")


                

    # --- TAB 2: TABLE VIEW ---
    with tab_table:
        st.info("📝 Advanced Mode: Edits here are auto-saved.")
        
        # Hide Verified column from editor but keep it for logic
        view_df = st.session_state.expenses.drop(columns=['Verified'])
        
        edited = st.data_editor(
            view_df,
            column_config={
                "Partner": st.column_config.SelectboxColumn(options=list(st.session_state.partners.keys()), required=True),
                "Category": st.column_config.SelectboxColumn(options=st.session_state.categories, required=True),
                "Amount": st.column_config.NumberColumn(format="$%.2f")
            },
            use_container_width=True,
            num_rows="dynamic",
            height=500
        )
        
        if not edited.equals(view_df):
            # If edited in table, we assume it's verified
            # We need to merge the edits back into the main DF which has the 'Verified' col
            # Reconstruct the DF
            edited['Verified'] = True
            st.session_state.expenses = edited
            st.rerun()

    # --- TAB 3: RESULTS ---
    with tab_results:
        st.header("📊 Final Reports")
        res_df = st.session_state.expenses
        
        if res_df.empty:
            st.warning("No data.")
        else:
            st.download_button("📥 Download Combined Report", 
                             data=generate_excel(res_df), 
                             file_name="Report.xlsx", 
                             type="primary")
            
            st.divider()
            cols = st.columns(len(st.session_state.partners))
            for i, (p, c) in enumerate(st.session_state.partners.items()):
                p_df = res_df[res_df['Partner'] == p]
                with cols[i]:
                    st.metric(p, f"${p_df['Amount'].sum():,.2f}")
                    if not p_df.empty:
                        st.download_button(f"📥 {p}", data=generate_excel(p_df), file_name=f"{p}.xlsx", key=f"dl_{p}")