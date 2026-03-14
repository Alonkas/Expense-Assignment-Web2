"""Minimal Streamlit app that wraps setup_page for testing."""
import streamlit as st
import pandas as pd
import datetime

if 'partners' not in st.session_state:
    st.session_state.partners = {}
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame()
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False
if 'categories' not in st.session_state:
    st.session_state.categories = []
if 'has_shared_partner' not in st.session_state:
    st.session_state.has_shared_partner = False
if 'category_rules' not in st.session_state:
    st.session_state.category_rules = {}
if 'verified_history' not in st.session_state:
    st.session_state.verified_history = []
if 'setup_step' not in st.session_state:
    st.session_state.setup_step = 1
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'detected_mapping' not in st.session_state:
    st.session_state.detected_mapping = None
if 'shares_shared' not in st.session_state:
    st.session_state.shares_shared = {}

# For partner-step tests: pre-populate with expense data and jump to step 3
if st.session_state.get('_test_jump_to_partners'):
    if st.session_state.setup_step == 1:
        st.session_state.expenses = pd.DataFrame({
            'Source': [''], 'Date': [datetime.date(2024, 1, 1)],
            'Description': ['Test'], 'Amount': [10.0],
            'Partner': [None], 'Category': ['Uncategorized'],
            'Comment': [''], 'Verified': [False],
        })
        st.session_state.setup_step = 3

from setup_page import render_setup_page
render_setup_page()
