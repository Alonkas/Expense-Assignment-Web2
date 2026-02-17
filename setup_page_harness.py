"""Minimal Streamlit app that wraps setup_page for testing."""
import streamlit as st
import pandas as pd

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

from setup_page import render_setup_page
render_setup_page()
