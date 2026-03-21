import html
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import generate_excel, calculate_shared_split, write_to_google_sheets, load_category_rules, save_category_rules, load_categories, save_categories
from setup_page import render_setup_page

# --- CONFIGURATION ---
st.set_page_config(page_title="Roommate Expense Manager", layout="wide", page_icon="🧾")

APP_VERSION = "Ver.4.5.0"

# --- INITIALIZE STATE ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame()
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
if 'partners' not in st.session_state:
    st.session_state.partners = {}
if 'categories' not in st.session_state:
    st.session_state.categories = load_categories()
if 'has_shared_partner' not in st.session_state:
    st.session_state.has_shared_partner = False
if 'shares_shared' not in st.session_state:
    st.session_state.shares_shared = {}
if 'setup_step' not in st.session_state:
    st.session_state.setup_step = 1
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'detected_mapping' not in st.session_state:
    st.session_state.detected_mapping = None
if 'category_rules' not in st.session_state:
    st.session_state.category_rules = load_category_rules()
if 'verified_history' not in st.session_state:
    st.session_state.verified_history = []
if 'rules_editing' not in st.session_state:
    st.session_state.rules_editing = False
if 'rules_edit_snapshot' not in st.session_state:
    st.session_state.rules_edit_snapshot = None

# --- ALWAYS DARK THEME ---
badge_bg = "rgba(30,30,30,0.8)"
card_bg = "#2d2d2d"
card_text = "#e0e0e0"
st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"] { background-color: #1e1e1e; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #2d2d2d; color: #e0e0e0; }
    [data-testid="stHeader"] { background-color: #1e1e1e; }
    .stTabs [data-baseweb="tab-panel"] { background-color: #1e1e1e; }
    .stTabs [data-baseweb="tab-list"] { background-color: #2d2d2d; }
    .stMarkdown, .stText, h1, h2, h3, h4, p, span, label, div { color: #e0e0e0 !important; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #e0e0e0 !important; }
    [data-testid="stMetricDelta"] { color: #aaa !important; }
    .stDataFrame { background-color: #2d2d2d; }
    </style>
""", unsafe_allow_html=True)

# Version badge
st.markdown(
    f"""
    <div style="position:fixed; bottom:10px; left:10px; z-index:9999;
        font-size:0.75em; color:#999; background:{badge_bg};
        padding:2px 8px; border-radius:4px;">
        {APP_VERSION}
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# HELPERS
# ==========================================

def _apply_view(df: pd.DataFrame, view: str) -> pd.DataFrame:
    if view == "Sum by category":
        return (
            df.groupby("Category", as_index=False)["Amount"]
            .sum()
            .sort_values("Amount", ascending=False)
            .rename(columns={"Amount": "Total"})
        )
    elif view == "By date (newest first)":
        return df.sort_values("Date", ascending=False).drop(columns=["Verified"], errors="ignore")
    elif view == "Most → least expensive":
        return df.sort_values("Amount", ascending=False).drop(columns=["Verified"], errors="ignore")
    else:  # Raw table (default)
        return df.drop(columns=["Verified"], errors="ignore")

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
            st.session_state.setup_step = 1
            st.rerun()

        st.divider()
        st.header("💰 Live Totals")

        current_totals = st.session_state.expenses.groupby("Partner")['Amount'].sum()

        has_shared = st.session_state.has_shared_partner
        shares_shared = st.session_state.shares_shared
        if has_shared:
            shared_total = current_totals.get("Shared", 0.0)
            sharing_partners = [p for p in st.session_state.partners if p != "Shared" and shares_shared.get(p, True)]
            num_sharing = len(sharing_partners)
            per_person_share = shared_total / num_sharing if num_sharing > 0 else 0.0

        for p, color in st.session_state.partners.items():
            amount = current_totals.get(p, 0.0)
            st.markdown(
                f"""
                <div style="padding:10px; margin-bottom:8px; background-color:{card_bg};
                    border-left: 6px solid {color}; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-weight:bold; font-size:0.9em; color:{card_text};">{html.escape(p)}</div>
                    <div style="font-size:1.2em; font-weight:bold;">{amount:,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if has_shared and p != "Shared" and shares_shared.get(p, True):
                st.markdown(
                    f"""
                    <div style="font-size:0.75em; color:#808080; margin-top:-4px; margin-bottom:8px; padding-left:16px;">
                        +{per_person_share:,.2f} from Shared
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()
        if st.button("🗑️ Reset All Data"):
            st.session_state.setup_complete = False
            st.session_state.expenses = pd.DataFrame()
            st.session_state.partners = {}
            st.session_state.has_shared_partner = False
            st.session_state.shares_shared = {}
            st.session_state.setup_step = 1
            st.session_state.raw_df = None
            st.session_state.detected_mapping = None
            st.rerun()

    st.title("Expense Dashboard")

    tab_focus, tab_table, tab_results, tab_rules, tab_cat_summary, tab_analytics = st.tabs([
        "🎯 Focus Mode (Verification)", "📊 Table View",
        "🏁 Final Results", "🏷️ Category Rules", "📋 Category Summary", "📈 Analytics"
    ])

    # --- TAB 1: FOCUS MODE ---
    with tab_focus:
        df = st.session_state.expenses

        if 'Verified' not in df.columns:
            df['Verified'] = False

        unverified_indices = df[df['Verified'] == False].index.tolist()

        if not unverified_indices:
            st.success("🎉 All expenses verified and assigned! Go to 'Final Results'.")
            if st.session_state.verified_history:
                if st.button("⬅️ Go Back", key="go_back_done_btn"):
                    prev_idx = st.session_state.verified_history.pop()
                    if prev_idx in st.session_state.expenses.index:
                        st.session_state.expenses.at[prev_idx, 'Verified'] = False
                    st.rerun()
        else:
            # Get current item
            curr_idx = unverified_indices[0]
            row = df.loc[curr_idx]

            # Progress Bar
            total_count = len(df)
            done_count = total_count - len(unverified_indices)
            st.progress(done_count / total_count, f"Reviewed: {done_count} / {total_count}")

            if st.session_state.verified_history:
                if st.button("⬅️ Go Back", key="go_back_btn"):
                    prev_idx = st.session_state.verified_history.pop()
                    if prev_idx in st.session_state.expenses.index:
                        st.session_state.expenses.at[prev_idx, 'Verified'] = False
                    st.rerun()

            # --- EXPENSE CARD ---
            st.markdown(f"""
            <div style="text-align:center; padding:30px; border-radius:15px; background:{card_bg};
                border:1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                {"<div style='display:inline-block; background:#444; color:#ccc; font-size:0.75em; padding:2px 8px; border-radius:8px; margin-bottom:6px;'>" + html.escape(str(row['Source'])) + "</div>" if row.get('Source') else ""}
                <div style="color:#888; font-size:1.1em; margin-bottom:5px;">{html.escape(str(row['Date']))}</div>
                <div style="font-size:1.8em; font-weight:bold; margin-bottom:10px;">{html.escape(str(row['Description']))}</div>
                <div style="font-size:2.5em; font-weight:900; color:{card_text};">{html.escape(f"{row['Amount']:.2f}")}</div>
            </div>
            """, unsafe_allow_html=True)

            # Suggestion Alert
            pre_filled_partner = row['Partner']
            if pre_filled_partner and pre_filled_partner in st.session_state.partners:
                st.info(f"💡 Excel suggests this belongs to **{pre_filled_partner}**. Click their name to confirm.")

            # --- AUTO-CATEGORIZATION MATCHING (exact match on full description) ---
            desc_lower = str(row['Description']).strip().lower()
            existing_cat = row['Category']
            has_category = pd.notna(existing_cat) and str(existing_cat).strip() and existing_cat != "Uncategorized"

            if has_category:
                matched_category = None  # respect existing category from Excel/Table View
            else:
                matched_category = st.session_state.category_rules.get(desc_lower)

            if matched_category:
                st.info(f"🏷️ Auto-category match: **{matched_category}** (change below if needed)")

            st.write("")

            # --- INPUTS ---
            c1, c2 = st.columns([1, 1])
            with c1:
                # Category Handling — prefer matched_category, then existing category
                if matched_category and matched_category in st.session_state.categories:
                    default_cat = matched_category
                else:
                    default_cat = row['Category'] if row['Category'] in st.session_state.categories else "Uncategorized"
                current_cat = default_cat

                cat_options = st.session_state.categories + ["➕ Add New..."]
                selected_cat = st.selectbox("Category", cat_options,
                                          index=st.session_state.categories.index(current_cat) if current_cat in st.session_state.categories else 0,
                                          key=f"cat_{curr_idx}")

                final_cat = selected_cat
                if selected_cat == "➕ Add New...":
                    new_cat_name = st.text_input("New Category Name", key=f"new_{curr_idx}")
                    if st.button("Save Cat"):
                        st.session_state.categories.append(new_cat_name)
                        save_categories(st.session_state.categories)
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
                            assigned_cat = final_cat if (final_cat and final_cat != "➕ Add New...") else "Uncategorized"
                            st.session_state.expenses.at[curr_idx, 'Partner'] = name
                            st.session_state.expenses.at[curr_idx, 'Category'] = assigned_cat
                            st.session_state.expenses.at[curr_idx, 'Comment'] = comment
                            st.session_state.expenses.at[curr_idx, 'Verified'] = True
                            st.session_state.verified_history.append(curr_idx)
                            # Auto-learn category rule
                            if assigned_cat and assigned_cat != "Uncategorized":
                                st.session_state.category_rules[desc_lower] = assigned_cat
                                save_category_rules(st.session_state.category_rules)
                            st.rerun()
            else:
                st.error("⚠️ No partners found! Please click 'Reset All Data' in the sidebar to setup partners.")


    # --- TAB 2: TABLE VIEW ---
    with tab_table:
        st.info("📝 Advanced Mode: Make your edits, then click Save.")

        # Hide Verified column from editor but keep it for logic
        view_df = st.session_state.expenses.drop(columns=['Verified'])

        edited = st.data_editor(
            view_df,
            column_config={
                "Partner": st.column_config.SelectboxColumn(options=list(st.session_state.partners.keys())),
                "Category": st.column_config.SelectboxColumn(options=st.session_state.categories),
                "Amount": st.column_config.NumberColumn(format="%.2f")
            },
            use_container_width=True,
            num_rows="dynamic",
            height=500
        )

        if st.button("💾 Save Changes", key="table_save_btn"):
            if not edited.equals(view_df):
                new_expenses = edited.copy()
                # Preserve existing Verified status; new rows default to False
                new_expenses['Verified'] = (
                    st.session_state.expenses['Verified']
                    .reindex(edited.index, fill_value=False)
                    .values
                )
                st.session_state.expenses = new_expenses.reset_index(drop=True)
                # Clear Go Back history since indices shifted
                st.session_state.verified_history = []
                # Clear cached Focus Mode widget state so edits appear
                for k in [k for k in st.session_state if k.startswith(('cat_', 'com_'))]:
                    del st.session_state[k]
                st.rerun()
            else:
                st.info("No changes to save.")

        # --- ADD NEW CATEGORY ---
        with st.expander("➕ Add New Category"):
            new_cat = st.text_input("Category Name", key="table_new_cat")
            if st.button("Add Category", key="table_add_cat_btn"):
                if new_cat and new_cat.strip() and new_cat.strip() not in st.session_state.categories:
                    st.session_state.categories.append(new_cat.strip())
                    save_categories(st.session_state.categories)
                    st.success(f"Category '{new_cat.strip()}' added.")
                    st.rerun()
                elif new_cat.strip() in st.session_state.categories:
                    st.warning("That category already exists.")
                else:
                    st.warning("Please enter a category name.")

    # --- TAB 3: RESULTS ---
    with tab_results:
        st.header("📊 Final Reports")
        res_df = st.session_state.expenses
        has_shared = st.session_state.has_shared_partner

        if res_df.empty:
            st.warning("No data.")
        else:
            shares_shared = st.session_state.shares_shared

            st.download_button("📥 Download Combined Report",
                             data=generate_excel(res_df, st.session_state.partners, has_shared, shares_shared),
                             file_name="Report.xlsx",
                             type="primary")

            if st.button("📤 Write to Google Sheets", type="secondary"):
                with st.spinner("Writing to Google Sheets..."):
                    try:
                        url = write_to_google_sheets(res_df, st.session_state.partners, has_shared, shares_shared)
                        st.success("Written to Google Sheets!")
                        st.markdown(f"[Open Google Sheet]({url})")
                    except Exception as e:
                        st.error(f"Failed to write to Google Sheets: {e}")

            st.divider()

            if has_shared:
                breakdown = calculate_shared_split(res_df, st.session_state.partners, has_shared, shares_shared)
                real_partners = breakdown['real_partners']
                sharing_partners = breakdown['sharing_partners']

                # --- Individual Totals ---
                st.subheader("Individual Totals (own expenses only)")
                ind_cols = st.columns(len(real_partners))
                for i, p in enumerate(real_partners):
                    color = st.session_state.partners.get(p, "#333")
                    with ind_cols[i]:
                        st.metric(p, f"{breakdown['individual_totals'][p]:,.2f}")

                st.divider()

                # --- Shared Total & Per-Person Share ---
                s1, s2 = st.columns(2)
                with s1:
                    st.metric("Shared Total", f"{breakdown['shared_total']:,.2f}")
                with s2:
                    st.metric(f"Per-Person Share (/{len(sharing_partners)})", f"{breakdown['per_person_share']:,.2f}")

                st.divider()

                # --- Grand Totals ---
                st.subheader("Grand Totals (individual + shared share)")
                grand_cols = st.columns(len(real_partners))
                for i, p in enumerate(real_partners):
                    with grand_cols[i]:
                        st.metric(p, f"{breakdown['grand_totals'][p]:,.2f}")
            else:
                # Original simple view
                cols = st.columns(len(st.session_state.partners))
                for i, (p, c) in enumerate(st.session_state.partners.items()):
                    p_df = res_df[res_df['Partner'] == p]
                    with cols[i]:
                        st.metric(p, f"{p_df['Amount'].sum():,.2f}")

            st.divider()

            # Per-partner download buttons
            for p in st.session_state.partners:
                p_df = res_df[res_df['Partner'] == p]
                if not p_df.empty:
                    st.download_button(f"📥 {p}", data=generate_excel(p_df), file_name=f"{p}.xlsx", key=f"dl_{p}")

    # --- TAB 4: CATEGORY RULES ---
    with tab_rules:
        st.header("🏷️ Category Rules")
        st.caption("Learned automatically when you verify expenses.")

        rules = st.session_state.category_rules
        editing = st.session_state.rules_editing

        # --- Action bar ---
        col_search, col_btn1, col_btn2, col_btn3 = st.columns([3, 1, 1, 1])
        with col_search:
            search = st.text_input("🔍", placeholder="Search rules...",
                                   label_visibility="collapsed", key="rules_search_input")
        save_clicked = cancel_clicked = False
        with col_btn1:
            if not editing:
                if st.button("✏️ Edit", use_container_width=True, disabled=not rules):
                    # Note: if Focus Mode writes a rule while editing is active,
                    # Cancel will revert that write. Acceptable trade-off.
                    st.session_state.rules_edit_snapshot = dict(rules)
                    st.session_state.rules_editing = True
                    st.rerun()
            else:
                save_clicked = st.button("💾 Save", use_container_width=True)
        with col_btn2:
            if editing:
                cancel_clicked = st.button("❌ Cancel", use_container_width=True)
        with col_btn3:
            if not editing:
                if st.button("🔄 Reload", use_container_width=True):
                    st.session_state.category_rules = load_category_rules()
                    st.toast("Rules reloaded from Google Sheets.")
                    st.rerun()

        # --- Add New Rule ---
        with st.expander("➕ Add New Rule"):
            if not editing:
                add_col1, add_col2, add_col3 = st.columns([2, 2, 1])
                with add_col1:
                    new_desc = st.text_input("Description", key="new_rule_desc",
                                             placeholder="e.g. supermarket purchase")
                with add_col2:
                    cat_options = st.session_state.categories or ["Uncategorized"]
                    new_cat = st.selectbox("Category", options=cat_options,
                                           key="new_rule_cat")
                with add_col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Add", use_container_width=True):
                        desc_key = new_desc.strip().lower()
                        if not desc_key:
                            st.warning("Description cannot be empty.")
                        elif desc_key in rules:
                            st.warning("A rule for this description already exists.")
                        else:
                            rules[desc_key] = new_cat
                            st.session_state.category_rules = rules
                            save_category_rules(rules)
                            st.toast("Rule added.")
                            st.rerun()
            else:
                st.info("Exit edit mode to add new rules.")

        # --- Rules table ---
        if rules:
            rules_data = [{"Description": k, "Category": v} for k, v in sorted(rules.items())]
            rules_df = pd.DataFrame(rules_data)

            # Apply search filter
            if search:
                mask = (rules_df["Description"].str.contains(search, case=False, na=False) |
                        rules_df["Category"].str.contains(search, case=False, na=False))
                display_df = rules_df[mask].reset_index(drop=True)
            else:
                display_df = rules_df

            filtered_keys = set(display_df["Description"].tolist())
            st.caption(f"Showing {len(display_df)} of {len(rules_df)} rules")

            if not editing:
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                edited_df = st.data_editor(
                    display_df,
                    column_config={
                        "Category": st.column_config.SelectboxColumn(
                            options=st.session_state.categories or ["Uncategorized"], required=True
                        )
                    },
                    use_container_width=True, hide_index=True, num_rows="dynamic",
                    key="rules_editor"
                )

                # Process Save/Cancel after editor renders
                if save_clicked:
                    new_rules = dict(rules)
                    for key in filtered_keys:
                        new_rules.pop(key, None)
                    for _, r in edited_df.iterrows():
                        desc = str(r["Description"]).strip().lower()
                        cat = str(r["Category"]).strip()
                        if desc and cat and cat.lower() != "nan":
                            new_rules[desc] = cat
                    st.session_state.category_rules = new_rules
                    save_category_rules(new_rules)
                    st.session_state.rules_editing = False
                    st.session_state.rules_edit_snapshot = None
                    st.toast("Rules saved.")
                    st.rerun()

                if cancel_clicked:
                    st.session_state.category_rules = st.session_state.rules_edit_snapshot
                    st.session_state.rules_editing = False
                    st.session_state.rules_edit_snapshot = None
                    st.rerun()
        else:
            st.info("No rules yet. Rules are learned automatically as you verify expenses.")

    # --- TAB 5: CATEGORY SUMMARY ---
    with tab_cat_summary:
        df = st.session_state.expenses
        partners = st.session_state.partners
        has_shared = st.session_state.has_shared_partner

        if df.empty:
            st.info("No expenses loaded yet.")
        else:
            real_partners = [p for p in partners if p != "Shared"]
            all_tab_partners = real_partners + (["Shared"] if has_shared else [])
            tab_labels = [f"👤 {p}" for p in real_partners] + (["⚖️ Shared"] if has_shared else [])

            cat_tabs = st.tabs(tab_labels)

            for cat_tab, partner in zip(cat_tabs, all_tab_partners):
                with cat_tab:
                    color = partners.get(partner, "#888")
                    partner_df = df[df['Partner'] == partner]

                    if partner_df.empty:
                        st.caption("No expenses for this partner.")
                    else:
                        total = partner_df['Amount'].sum()
                        cat_sums = (
                            partner_df.groupby("Category", as_index=False)["Amount"]
                            .sum()
                            .sort_values("Amount", ascending=False)
                        )
                        cat_sums["% of Total"] = (cat_sums["Amount"] / total * 100).round(1)

                        # Summary table with total row
                        display_df = cat_sums.copy()
                        total_row = pd.DataFrame([{
                            "Category": "Total",
                            "Amount": total,
                            "% of Total": 100.0,
                        }])
                        display_df = pd.concat([display_df, total_row], ignore_index=True)

                        st.markdown(
                            f'<div style="font-size:1.4em; font-weight:800; color:{color}; margin-bottom:12px;">'
                            f'{html.escape(partner)} — Total: {total:,.2f}</div>',
                            unsafe_allow_html=True
                        )
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Amount": st.column_config.NumberColumn(format="%.2f"),
                                "% of Total": st.column_config.NumberColumn(format="%.1f%%"),
                            },
                        )

                        # Pie chart
                        fig = px.pie(
                            cat_sums, names="Category", values="Amount",
                            title=f"{partner}'s expenses by category",
                            template="plotly_dark",
                        )
                        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 6: ANALYTICS ---
    with tab_analytics:
        df = st.session_state.expenses
        partners = st.session_state.partners
        has_shared = st.session_state.has_shared_partner

        if df.empty:
            st.info("No expenses loaded yet.")
        else:
            real_partners = [p for p in partners if p != "Shared"]
            all_tab_partners = real_partners + (["Shared"] if has_shared else [])
            tab_labels = [f"👤 {p}" for p in real_partners] + (["⚖️ Shared"] if has_shared else [])

            partner_tabs = st.tabs(tab_labels)

            for tab, partner in zip(partner_tabs, all_tab_partners):
                with tab:
                    color = partners.get(partner, "#888")
                    own_df = df[df['Partner'] == partner].copy()
                    # Shared section: only shown inside real partner tabs
                    shared_df = (
                        df[df['Partner'] == "Shared"].copy()
                        if has_shared and partner != "Shared"
                        else pd.DataFrame()
                    )

                    # View selector
                    view = st.selectbox(
                        "View",
                        ["Raw table", "Sum by category", "By date (newest first)", "Most → least expensive", "Pie by category"],
                        key=f"analytics_view_{partner}"
                    )

                    # Total metric
                    total = own_df['Amount'].sum()
                    st.markdown(
                        f'<div style="font-size:1.4em; font-weight:800; color:{color}; margin-bottom:12px;">'
                        f'Total: {total:,.2f}</div>',
                        unsafe_allow_html=True
                    )

                    # Own expenses
                    st.markdown(f"**{html.escape(partner)}'s expenses**")
                    if own_df.empty:
                        st.caption("No expenses.")
                    else:
                        if view == "Pie by category":
                            cat_sums = own_df.groupby("Category", as_index=False)["Amount"].sum()
                            fig = px.pie(cat_sums, names="Category", values="Amount",
                                         title=f"{partner}'s expenses by category",
                                         template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.dataframe(_apply_view(own_df, view), use_container_width=True, hide_index=True)
                            st.markdown(
                                f'<div style="text-align:right; color:{color}; font-weight:700; margin-top:4px;">'
                                f'Sum: {own_df["Amount"].sum():,.2f}</div>',
                                unsafe_allow_html=True
                            )

                    # Shared expenses (real partners only)
                    if not shared_df.empty:
                        st.markdown("---")
                        st.markdown("**Shared expenses** *(full amounts)*")
                        if view == "Pie by category":
                            cat_sums = shared_df.groupby("Category", as_index=False)["Amount"].sum()
                            fig = px.pie(cat_sums, names="Category", values="Amount",
                                         title="Shared expenses by category",
                                         template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.dataframe(_apply_view(shared_df, view), use_container_width=True, hide_index=True)
                            shared_total = shared_df["Amount"].sum()
                            st.markdown(
                                f'<div style="text-align:right; color:#aaa; font-weight:700; margin-top:4px;">'
                                f'Sum: {shared_total:,.2f}</div>',
                                unsafe_allow_html=True
                            )
