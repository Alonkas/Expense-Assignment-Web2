import html
import streamlit as st
import pandas as pd
from utils import generate_excel, calculate_shared_split, write_to_google_sheets, load_category_rules, save_category_rules, load_categories, save_categories
from setup_page import render_setup_page

# --- CONFIGURATION ---
st.set_page_config(page_title="Roommate Expense Manager", layout="wide", page_icon="🧾")

APP_VERSION = "Ver. 4.0.0 (Modern Dark UI)"

# --- INITIALIZE STATE ---
if 'expenses' not in st.session_state: st.session_state.expenses = pd.DataFrame()
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'partners' not in st.session_state: st.session_state.partners = {}
if 'categories' not in st.session_state: st.session_state.categories = load_categories()
if 'has_shared_partner' not in st.session_state: st.session_state.has_shared_partner = False
# Note: Removed 'dark_mode' state as we are forcing a curated dark theme.
if 'category_rules' not in st.session_state: st.session_state.category_rules = load_category_rules()
if 'verified_history' not in st.session_state: st.session_state.verified_history = []


# ==========================================
#  GLOBAL MODERN DARK THEME CSS
# ==========================================
st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">

    <style>
    /* --- VARIABLES --- */
    :root {{
        --bg-main: #0e0e10;
        --bg-secondary: #18181b;
        --card-bg: #222226;
        --text-primary: #efeff1;
        --text-secondary: #adadb8;
        --accent-color: #00C9FF; /* Cyan accent */
        --accent-gradient: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
        --danger-color: #ff4757;
        --success-color: #2ed573;
    }}

    /* --- BASE STYLES --- */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }}

    .stApp {{
        background-color: var(--bg-main);
    }}

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-secondary);
        border-right: 1px solid #2d2d30;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: var(--text-primary) !important;
        font-weight: 600;
        letter-spacing: -0.5px;
    }}

    /* --- HEADERS & TEXT --- */
    h1, h2, h3 {{
        font-weight: 800 !important;
        letter-spacing: -1px !important;
    }}
    p, label, .stMarkdown {{
        color: var(--text-secondary) !important;
    }}

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid var(--bg-secondary);
        padding-bottom: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        white-space: nowrap;
        background-color: var(--bg-secondary);
        border-radius: 8px;
        color: var(--text-secondary);
        border: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: var(--card-bg) !important;
        color: var(--accent-color) !important;
        border: 1px solid var(--accent-color) !important;
    }}

    /* --- INPUTS & WIDGETS --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] div, .stNumberInput input, .stTextArea textarea {{
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }}
    /* Focus states for inputs */
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within div {{
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 1px var(--accent-color) !important;
    }}

    /* --- BUTTONS --- */
    /* Primary Button (Gradient Pill) */
    div.stButton > button[kind="primary"] {{
        background: var(--accent-gradient) !important;
        border: none !important;
        color: #000 !important;
        font-weight: 800 !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.5rem !important;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    div.stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 201, 255, 0.3);
    }}
    /* Secondary Button (Outline Pill) */
    div.stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        border: 2px solid #444 !important;
        color: var(--text-primary) !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        border-color: var(--text-primary) !important;
        background-color: var(--bg-secondary) !important;
    }}

    /* --- DATAFRAME --- */
    [data-testid="stDataFrame"] {{
        border: 1px solid #333;
        border-radius: 12px;
        overflow: hidden;
    }}
    [data-testid="stDataFrame"] th {{
        background-color: var(--card-bg) !important;
        color: var(--text-secondary) !important;
    }}
    [data-testid="stDataFrame"] td {{
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-bottom: 1px solid #333 !important;
    }}

    /* --- METRICS --- */
    [data-testid="stMetricValue"] {{
        color: var(--accent-color) !important;
        font-weight: 800 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--text-secondary) !important;
    }}

    /* --- ALERTS --- */
    .stAlert {{
        background-color: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
    }}
    </style>
""", unsafe_allow_html=True)


# Version badge (Styled)
st.markdown(
    f"""
    <div style="position:fixed; bottom:15px; left:20px; z-index:9999;
        font-size:0.7em; font-weight: 600; color: var(--text-secondary);
        background: var(--card-bg); border: 1px solid #333;
        padding: 4px 10px; border-radius: 50px;">
        {APP_VERSION}
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# FLOW CONTROL
# ==========================================

if not st.session_state.setup_complete:
    render_setup_page()
else:
    # --- SIDEBAR: LIVE TOTALS & ACTIONS ---
    with st.sidebar:
        st.header("Actions")
        if st.button("📂 Add More Files", type="secondary", use_container_width=True):
            st.session_state.setup_complete = False
            st.rerun()

        st.divider()
        st.header("Wallet Balances")

        current_totals = st.session_state.expenses.groupby("Partner")['Amount'].sum()

        has_shared = st.session_state.has_shared_partner
        if has_shared:
            shared_total = current_totals.get("Shared", 0.0)
            num_real_partners = len(st.session_state.partners) - 1
            per_person_share = shared_total / num_real_partners if num_real_partners > 0 else 0.0

        for p, color in st.session_state.partners.items():
            amount = current_totals.get(p, 0.0)
            # Modern Sidebar Card Design
            st.markdown(
                f"""
                <div style="padding: 15px; margin-bottom: 12px;
                    background-color: var(--card-bg);
                    border-radius: 12px;
                    border-left: 4px solid {color};
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight:600; font-size:0.9em; color:var(--text-secondary);">{html.escape(p)}</div>
                        <div style="font-size:1.4em; font-weight:800; color:var(--text-primary);">{amount:,.2f}</div>
                    </div>
                    {'<div style="font-size:1.5em;">💰</div>' if p != 'Shared' else '<div style="font-size:1.5em;">⚖️</div>'}
                </div>
                """,
                unsafe_allow_html=True
            )
            if has_shared and p != "Shared":
                 st.markdown(
                    f"""<div style="font-size:0.7em; color:var(--text-secondary); margin-top:-8px; margin-bottom:12px; text-align:right; padding-right: 10px;">
                        + {per_person_share:,.2f} (Shared)
                    </div>""", unsafe_allow_html=True)

        st.divider()
        st.warning("Danger Zone")
        if st.button("🗑️ Reset All Data", type="secondary", use_container_width=True):
            st.session_state.setup_complete = False
            st.session_state.expenses = pd.DataFrame()
            st.session_state.partners = {}
            st.session_state.has_shared_partner = False
            st.rerun()

    # Main Content Area
    st.title("Expense Dashboard")
    st.caption("Review, categorize, and split your imported expenses.")

    tab_focus, tab_table, tab_results, tab_rules = st.tabs(["🎯 Focus Mode", "📊 Table View", "🏁 Final Results", "🏷️ Category Rules"])

    # --- TAB 1: FOCUS MODE (The "Hero" Section) ---
    with tab_focus:
        df = st.session_state.expenses

        if 'Verified' not in df.columns:
            df['Verified'] = False

        unverified_indices = df[df['Verified'] == False].index.tolist()

        if not unverified_indices:
            # Success State Design
            st.markdown("""
                <div style="text-align:center; padding: 50px 20px;">
                    <h1 style="font-size: 3em; margin-bottom: 10px;">🎉</h1>
                    <h2 style="color: var(--accent-color);">All Caught Up!</h2>
                    <p>Every expense has been verified. Head over to the <b>Final Results</b> tab.</p>
                </div>
            """, unsafe_allow_html=True)

            if st.session_state.verified_history:
                st.divider()
                if st.button("⬅️ Undo Last Verification", key="go_back_done_btn", type="secondary"):
                    prev_idx = st.session_state.verified_history.pop()
                    st.session_state.expenses.at[prev_idx, 'Verified'] = False
                    st.rerun()
        else:
            # Get current item
            curr_idx = unverified_indices[0]
            row = df.loc[curr_idx]

            # Progress Bar (Custom label styling)
            total_count = len(df)
            done_count = total_count - len(unverified_indices)
            st.caption(f"PROGRESS: REVIEWED {done_count} OF {total_count}")
            st.progress(done_count / total_count)

            # Top controls
            if st.session_state.verified_history:
                 if st.button("⬅️ Undo", key="go_back_btn", type="secondary"):
                    prev_idx = st.session_state.verified_history.pop()
                    st.session_state.expenses.at[prev_idx, 'Verified'] = False
                    st.rerun()

            st.write("") # Spacer

            # --- MODERN EXPENSE HERO CARD ---
            st.markdown(f"""
            <div style="
                text-align:center;
                padding: 40px 20px;
                border-radius: 24px;
                background: linear-gradient(160deg, var(--card-bg) 0%, var(--bg-secondary) 100%);
                border: 1px solid #333;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                margin-bottom: 25px;
                position: relative;
                overflow: hidden;
            ">
                <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: radial-gradient(circle, rgba(0,201,255,0.05) 0%, rgba(0,0,0,0) 70%); pointer-events:none;"></div>

                <div style="position: relative; z-index: 2;">
                    <div style="color: var(--text-secondary); font-weight: 600; letter-spacing: 1px; text-transform: uppercase; font-size: 0.8em; margin-bottom: 10px;">
                        📅 {html.escape(str(row['Date']))}
                    </div>
                    <h2 style="font-size: 1.8em; font-weight: 700; margin: 0 0 15px 0; color: var(--text-primary); line-height: 1.2;">
                        {html.escape(str(row['Description']))}
                    </h2>
                    <h1 style="
                        font-size: 4.5em;
                        font-weight: 900;
                        margin: 0;
                        background: var(--accent-gradient);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        letter-spacing: -2px;
                    ">
                        {row['Amount']:.2f}
                    </h1>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Info Alerts (Styled by global CSS)
            pre_filled_partner = row['Partner']
            if pre_filled_partner and pre_filled_partner in st.session_state.partners:
                st.info(f"💡 Suggestion: Looks like **{pre_filled_partner}** based on the file.")

            desc_lower = str(row['Description']).strip().lower()
            matched_category = st.session_state.category_rules.get(desc_lower)
            if matched_category:
                st.success(f"🏷️ Auto-Category: Matched to **{matched_category}**.")

            st.write("")

            # --- INPUTS CONTAINER ---
            with st.container():
                c1, c2 = st.columns([1, 1])
                with c1:
                    # Category Logic
                    if matched_category and matched_category in st.session_state.categories:
                        default_cat = matched_category
                    else:
                        default_cat = row['Category'] if row['Category'] in st.session_state.categories else "Uncategorized"
                    current_cat = default_cat

                    cat_options = st.session_state.categories + ["➕ Add New..."]
                    selected_cat = st.selectbox("🏷️ Category", cat_options,
                                              index=st.session_state.categories.index(current_cat) if current_cat in st.session_state.categories else 0,
                                              key=f"cat_{curr_idx}")

                    final_cat = selected_cat
                    if selected_cat == "➕ Add New...":
                        new_cat_name = st.text_input("Name of New Category", key=f"new_{curr_idx}")
                        if st.button("Save Category", type="primary"):
                            st.session_state.categories.append(new_cat_name)
                            save_categories(st.session_state.categories)
                            st.rerun()
                        final_cat = new_cat_name

                with c2:
                    comment = st.text_input("💬 Comment (Optional)", value=str(row['Comment']), key=f"com_{curr_idx}")

            st.divider()

            # --- DYNAMIC PARTNER BUTTONS ---
            st.subheader("👇 Assign To:")

            partners = list(st.session_state.partners.items())
            num_p = len(partners)

            if num_p > 0:
                num_cols = min(num_p, 4)
                cols = st.columns(num_cols)

                for i, (name, color) in enumerate(partners):
                    col_idx = i % num_cols
                    with cols[col_idx]:
                        is_suggested = (name == pre_filled_partner)
                        label = f"✅ {name}" if is_suggested else name
                        # Use primary style for suggestion, secondary for others
                        type_btn = "primary" if is_suggested else "secondary"

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
                st.error("⚠️ Missing partner data. Please reset.")


    # --- TAB 2: TABLE VIEW ---
    with tab_table:
        st.caption("Advanced Mode: Bulk edit data directly in the grid.")

        view_df = st.session_state.expenses.drop(columns=['Verified'])

        edited = st.data_editor(
            view_df,
            column_config={
                "Partner": st.column_config.SelectboxColumn(options=list(st.session_state.partners.keys()), required=True),
                "Category": st.column_config.SelectboxColumn(options=st.session_state.categories, required=True),
                "Amount": st.column_config.NumberColumn(format="%.2f")
            },
            use_container_width=True,
            num_rows="dynamic",
            height=500
        )

        if not edited.equals(view_df):
            edited['Verified'] = True
            st.session_state.expenses = edited
            st.rerun()

        with st.expander("➕ Quickly Add Category"):
            c_add1, c_add2 = st.columns([3,1])
            new_cat = c_add1.text_input("Category Name", key="table_new_cat", label_visibility="collapsed", placeholder="New Category Name...")
            if c_add2.button("Add", key="table_add_cat_btn", type="primary", use_container_width=True):
                if new_cat and new_cat.strip() and new_cat.strip() not in st.session_state.categories:
                    st.session_state.categories.append(new_cat.strip())
                    save_categories(st.session_state.categories)
                    st.toast(f"Category '{new_cat.strip()}' added!", icon="✅")
                    st.rerun()

    # --- TAB 3: RESULTS ---
    with tab_results:
        res_df = st.session_state.expenses
        has_shared = st.session_state.has_shared_partner

        if res_df.empty:
            st.warning("No data available yet.")
        else:
            # Header Actions
            c_dl1, c_dl2 = st.columns(2)
            c_dl1.download_button("📥 Download Excel Report",
                             data=generate_excel(res_df, st.session_state.partners, has_shared),
                             file_name="Report.xlsx",
                             type="primary", use_container_width=True)

            if c_dl2.button("📤 Sync to Google Sheets", type="secondary", use_container_width=True):
                with st.spinner("Syncing data..."):
                    try:
                        url = write_to_google_sheets(res_df, st.session_state.partners, has_shared)
                        st.toast("Sync successful!", icon="🚀")
                        st.markdown(f"**Link:** [Open Google Sheet]({url})")
                    except Exception as e:
                        st.error(f"Sync Failed: {e}")

            st.divider()

            if has_shared:
                breakdown = calculate_shared_split(res_df, st.session_state.partners, has_shared)
                real_partners = breakdown['real_partners']

                st.subheader("Individual Spending (Directly assigned)")
                ind_cols = st.columns(len(real_partners))
                for i, p in enumerate(real_partners):
                    with ind_cols[i]:
                        st.metric(p, f"{breakdown['individual_totals'][p]:,.2f}")

                st.divider()

                # Modern Shared Section styling
                st.markdown(f"""
                <div style="background: var(--card-bg); padding: 20px; border-radius: 16px; border: 1px solid #333;">
                    <h3 style="margin-top:0;">⚖️ The Split</h3>
                    <div style="display: flex; gap: 40px;">
                        <div>
                            <div style="color:var(--text-secondary); font-size: 0.9em;">Total Shared Pot</div>
                            <div style="font-size: 2em; font-weight: 900; color: var(--accent-color);">{breakdown['shared_total']:,.2f}</div>
                        </div>
                        <div>
                            <div style="color:var(--text-secondary); font-size: 0.9em;">Per Person (/{len(real_partners)})</div>
                            <div style="font-size: 2em; font-weight: 900; color: var(--text-primary);">{breakdown['per_person_share']:,.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.divider()

                st.subheader("🏁 Grand Totals (Final Owed)")
                grand_cols = st.columns(len(real_partners))
                for i, p in enumerate(real_partners):
                    color = st.session_state.partners.get(p, var(--accent-color))
                    with grand_cols[i]:
                         st.markdown(f"""
                            <div style="border-bottom: 4px solid {color}; padding-bottom: 10px;">
                                <div style="color:var(--text-secondary); font-size: 0.9em;">{p}</div>
                                <div style="font-size: 2.2em; font-weight: 900; color: var(--text-primary);">{breakdown['grand_totals'][p]:,.2f}</div>
                            </div>
                        """, unsafe_allow_html=True)

            else:
                # Simple View
                cols = st.columns(len(st.session_state.partners))
                for i, (p, c) in enumerate(st.session_state.partners.items()):
                    p_df = res_df[res_df['Partner'] == p]
                    with cols[i]:
                        st.metric(p, f"{p_df['Amount'].sum():,.2f}")

            st.divider()
            with st.expander("📂 Individual Partner Downloads"):
                for p in st.session_state.partners:
                    p_df = res_df[res_df['Partner'] == p]
                    if not p_df.empty:
                        st.download_button(f"📥 Download {p}.xlsx", data=generate_excel(p_df), file_name=f"{p}.xlsx", key=f"dl_{p}")

    # --- TAB 4: CATEGORY RULES ---
    with tab_rules:
        st.caption("These rules are learned automatically. Edit them here to refine auto-categorization.")

        rules = st.session_state.category_rules
        if rules:
            rules_data = [{"Description": k, "Category": v} for k, v in sorted(rules.items())]
            rules_df = pd.DataFrame(rules_data)
            edited_rules = st.data_editor(
                rules_df,
                column_config={
                    "Description": st.column_config.TextColumn(disabled=True),
                    "Category": st.column_config.SelectboxColumn(
                        options=st.session_state.categories, required=True
                    )
                },
                use_container_width=True, hide_index=True, num_rows="fixed", height=400,
                key="rules_editor"
            )
            # Sync edits back
            if not edited_rules.equals(rules_df):
                new_rules = {}
                for _, r in edited_rules.iterrows():
                    desc = str(r["Description"]).strip().lower()
                    cat = str(r["Category"]).strip()
                    if desc and cat:
                        new_rules[desc] = cat
                st.session_state.category_rules = new_rules
                save_category_rules(new_rules)
                st.rerun()
        else:
             st.markdown("""
                <div style="text-align:center; padding: 40px; background: var(--card-bg); border-radius: 12px; color: var(--text-secondary);">
                    Start verifying expenses in Focus Mode, and rules will appear here automatically.
                </div>
            """, unsafe_allow_html=True)