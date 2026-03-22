import streamlit as st
import pandas as pd
from utils import auto_detect_columns, apply_mapping, extract_categories, save_categories, SHARED_KEYWORDS


DEFAULT_COLORS = ["#FF4B4B", "#1E90FF", "#228B22", "#FFA500", "#9370DB", "#008080", "#FF1493"]
DEFAULT_NAMES = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]


def _cleanup_wizard_state():
    """Remove temporary wizard keys from session state."""
    for key in ['raw_df', 'detected_mapping', 'setup_step', 'wiz_partner_list', '_wiz_next_id']:
        st.session_state.pop(key, None)


def render_setup_page():
    st.title("Expense App Setup")

    step = st.session_state.get('setup_step', 1)

    # Progress indicator
    labels = ["Upload", "Map Columns", "Partners"]
    cols = st.columns(len(labels))
    for i, label in enumerate(labels):
        s = i + 1
        if s < step:
            cols[i].markdown(f"~~:gray[{s}. {label}]~~")
        elif s == step:
            cols[i].markdown(f"**{s}. {label}**")
        else:
            cols[i].markdown(f":gray[{s}. {label}]")

    st.divider()

    if step == 1:
        _step_upload()
    elif step == 2:
        _step_column_mapping()
    elif step == 3:
        _step_partners()


def _step_upload():
    st.subheader("1. Upload Excel File")
    st.caption("Upload an Excel file (.xlsx / .xls) with your expenses.")

    uploaded_file = st.file_uploader(
        "Choose file", type=['xlsx', 'xls'], key="wizard_uploader"
    )

    if uploaded_file:
        try:
            raw_df = pd.read_excel(uploaded_file)
            st.session_state.raw_df = raw_df
            st.session_state.detected_mapping = auto_detect_columns(raw_df)
            st.session_state.setup_step = 2
            st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")


def _step_column_mapping():
    if st.button("Back", key="back_to_1"):
        st.session_state.setup_step = 1
        st.session_state.pop('raw_df', None)
        st.session_state.pop('detected_mapping', None)
        st.rerun()

    st.subheader("2. Confirm Column Mapping")

    raw_df = st.session_state.get('raw_df')
    if raw_df is None:
        st.session_state.setup_step = 1
        st.rerun()
        return

    detected = st.session_state.get('detected_mapping', {})
    columns = raw_df.columns.tolist()
    opt_cols = ["None"] + columns

    def _default_index(field, options):
        val = detected.get(field)
        if val and val in options:
            return options.index(val)
        return 0

    st.caption("Required fields are marked with *")
    c1, c2 = st.columns(2)
    with c1:
        date_col = st.selectbox("Date *", columns, index=_default_index('date', columns), key="map_date")
        desc_col = st.selectbox("Description *", columns, index=_default_index('desc', columns), key="map_desc")
        amt_col = st.selectbox("Amount *", columns, index=_default_index('amt', columns), key="map_amt")
        source_col = st.selectbox("Source (Credit Card)", opt_cols, index=_default_index('source', opt_cols), key="map_source")
    with c2:
        partner_col = st.selectbox("Partner", opt_cols, index=_default_index('partner', opt_cols), key="map_partner")
        cat_col = st.selectbox("Category", opt_cols, index=_default_index('cat', opt_cols), key="map_cat")
        comment_col = st.selectbox("Comment", opt_cols, index=_default_index('comment', opt_cols), key="map_comment")

    st.markdown("**Preview (first 5 rows):**")
    st.dataframe(raw_df.head(5), use_container_width=True, hide_index=True)

    if st.button("Confirm Mapping", type="primary"):
        mapping = {
            'date': date_col, 'desc': desc_col, 'amt': amt_col,
            'source': source_col, 'partner': partner_col,
            'cat': cat_col, 'comment': comment_col
        }
        cleaned = apply_mapping(raw_df.copy(), mapping)

        # Extract categories
        imported_cats = extract_categories(cleaned)
        for cat in imported_cats:
            if cat not in st.session_state.categories:
                st.session_state.categories.append(cat)
        save_categories(st.session_state.categories)

        # Append to expenses
        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, cleaned], ignore_index=True
        )

        # Skip partner config if partners already exist (Add More Files flow)
        if st.session_state.partners:
            st.session_state.setup_complete = True
            _cleanup_wizard_state()
        else:
            st.session_state.setup_step = 3
        st.rerun()


def _step_partners():
    if st.button("Back", key="back_to_2"):
        # Undo the appended data from step 2
        st.session_state.pop('wiz_partner_list', None)
        st.session_state.pop('_wiz_next_id', None)
        st.session_state.setup_step = 2
        st.rerun()

    st.subheader("3. Configure Partners")

    df = st.session_state.expenses
    has_partner_data = 'Partner' in df.columns and df['Partner'].notna().any()

    if has_partner_data:
        # Auto-detect partners from the mapped column
        unique_partners = df['Partner'].dropna().unique().tolist()
        unique_partners = [str(p).strip() for p in unique_partners if str(p).strip()]

        # Check for shared partner in data
        shared_found = None
        for p in unique_partners:
            if p.lower() in SHARED_KEYWORDS:
                shared_found = p

        # Initialize working list once from detected data (dicts with stable IDs)
        if 'wiz_partner_list' not in st.session_state:
            filtered = [p for p in unique_partners if p.lower() not in SHARED_KEYWORDS]
            st.session_state.wiz_partner_list = [
                {'id': idx, 'name': p} for idx, p in enumerate(filtered)
            ]
            st.session_state._wiz_next_id = len(filtered)

        partner_list = st.session_state.wiz_partner_list

        st.info(f"Detected {len(unique_partners)} partner(s) from your data: {', '.join(unique_partners)}")

        # Build partner dict with auto-assigned colors
        current_partners = {}
        shares_shared = {}

        # Editable partner list with remove buttons
        st.markdown("**Edit partner names and colors:**")
        for i, entry in enumerate(partner_list):
            pid = entry['id']
            color = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
            c_name, c_color, c_remove = st.columns([3, 1, 1])
            with c_name:
                name = st.text_input(f"Partner {i+1}", value=entry['name'], key=f"wiz_pname_{pid}")
            with c_color:
                pcolor = st.color_picker(f"Color {i+1}", color, key=f"wiz_pcol_{pid}")
            with c_remove:
                st.write("")  # vertical spacer to align with inputs
                if len(partner_list) > 1:
                    if st.button("Remove", key=f"wiz_remove_{pid}"):
                        st.session_state.wiz_partner_list.pop(i)
                        st.rerun()
            current_partners[name] = pcolor

        # Add extra partner
        if st.button("+ Add Partner"):
            nid = st.session_state._wiz_next_id
            st.session_state._wiz_next_id = nid + 1
            idx = len(partner_list)
            new_name = DEFAULT_NAMES[idx] if idx < len(DEFAULT_NAMES) else f"Partner {idx+1}"
            st.session_state.wiz_partner_list.append({'id': nid, 'name': new_name})
            st.rerun()

        # Shared toggle — pre-check if shared keyword found
        enable_shared = st.toggle(
            "Enable a 'Shared' partner for joint expenses?",
            value=shared_found is not None, key="wiz_shared_toggle"
        )
        if enable_shared:
            for name in current_partners:
                shares_shared[name] = st.toggle(
                    f"{name} shares Shared?", value=True, key=f"wiz_shares_{name}"
                )
    else:
        # Manual entry fallback — no partner column
        st.caption("No partner column was detected. Set up partners manually.")
        num_partners = st.slider("How many roommates?", min_value=1, max_value=7, value=2, key="wiz_num_partners")

        current_partners = {}
        shares_shared = {}
        cols = st.columns(3)
        for i in range(num_partners):
            with cols[i % 3]:
                name = st.text_input(f"Name {i+1}", value=DEFAULT_NAMES[i], key=f"wiz_mp_name_{i}")
                color = st.color_picker(f"Color {i+1}", DEFAULT_COLORS[i], key=f"wiz_mp_col_{i}")
                current_partners[name] = color

        enable_shared = st.toggle("Enable a 'Shared' partner for joint expenses?", key="wiz_shared_toggle_manual")
        if enable_shared:
            for name in current_partners:
                shares_shared[name] = st.toggle(
                    f"{name} shares Shared?", value=True, key=f"wiz_shares_m_{name}"
                )
        shared_found = None

    if st.button("Confirm Partners", type="primary"):
        st.session_state.partners = current_partners
        if enable_shared:
            st.session_state.partners["Shared"] = "#808080"
            st.session_state.has_shared_partner = True
            st.session_state.shares_shared = shares_shared
        else:
            st.session_state.has_shared_partner = False
            st.session_state.shares_shared = {}
        st.session_state.setup_complete = True
        _cleanup_wizard_state()
        st.rerun()
