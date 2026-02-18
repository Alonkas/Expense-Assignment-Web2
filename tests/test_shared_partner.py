import io
import pytest
import pandas as pd
import datetime
from utils import calculate_shared_split, generate_excel


# --- Helper to build a test DataFrame ---
def make_expenses(rows):
    """Build an expenses DataFrame from a list of (partner, amount) tuples."""
    records = []
    for i, (partner, amount) in enumerate(rows):
        records.append({
            'Date': datetime.date(2025, 1, i + 1),
            'Description': f'Item {i + 1}',
            'Amount': amount,
            'Partner': partner,
            'Category': 'Groceries',
            'Comment': '',
            'Verified': True,
        })
    return pd.DataFrame(records)


# =============================================
# Unit tests for calculate_shared_split
# =============================================

class TestCalculateSharedSplit:
    def test_basic_shared_split(self):
        """Two real partners + shared expenses split equally."""
        df = make_expenses([
            ('Alice', 100),
            ('Bob', 200),
            ('Shared', 60),
        ])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF', 'Shared': '#808080'}
        result = calculate_shared_split(df, partners, has_shared_partner=True)

        assert result['individual_totals'] == {'Alice': 100.0, 'Bob': 200.0}
        assert result['shared_total'] == 60.0
        assert result['per_person_share'] == 30.0
        assert result['grand_totals'] == {'Alice': 130.0, 'Bob': 230.0}
        assert result['real_partners'] == ['Alice', 'Bob']

    def test_no_shared_partner_flag(self):
        """When has_shared_partner=False, returns simple totals with zero shared."""
        df = make_expenses([
            ('Alice', 100),
            ('Bob', 200),
        ])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF'}
        result = calculate_shared_split(df, partners, has_shared_partner=False)

        assert result['shared_total'] == 0.0
        assert result['per_person_share'] == 0.0
        assert result['grand_totals'] == {'Alice': 100.0, 'Bob': 200.0}

    def test_zero_shared_expenses(self):
        """Shared partner enabled but no expenses assigned to Shared."""
        df = make_expenses([
            ('Alice', 50),
            ('Bob', 75),
        ])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF', 'Shared': '#808080'}
        result = calculate_shared_split(df, partners, has_shared_partner=True)

        assert result['shared_total'] == 0.0
        assert result['per_person_share'] == 0.0
        assert result['grand_totals'] == {'Alice': 50.0, 'Bob': 75.0}

    def test_three_partners_shared(self):
        """Three real partners split shared expenses equally."""
        df = make_expenses([
            ('Alice', 100),
            ('Bob', 200),
            ('Charlie', 300),
            ('Shared', 90),
        ])
        partners = {
            'Alice': '#FF0000', 'Bob': '#0000FF',
            'Charlie': '#00FF00', 'Shared': '#808080',
        }
        result = calculate_shared_split(df, partners, has_shared_partner=True)

        assert result['shared_total'] == 90.0
        assert result['per_person_share'] == 30.0
        assert result['grand_totals']['Alice'] == 130.0
        assert result['grand_totals']['Bob'] == 230.0
        assert result['grand_totals']['Charlie'] == 330.0

    def test_single_real_partner(self):
        """Single real partner gets all shared expenses."""
        df = make_expenses([
            ('Alice', 100),
            ('Shared', 50),
        ])
        partners = {'Alice': '#FF0000', 'Shared': '#808080'}
        result = calculate_shared_split(df, partners, has_shared_partner=True)

        assert result['per_person_share'] == 50.0
        assert result['grand_totals']['Alice'] == 150.0

    def test_multiple_shared_expenses(self):
        """Multiple shared rows sum up correctly."""
        df = make_expenses([
            ('Alice', 100),
            ('Bob', 50),
            ('Shared', 30),
            ('Shared', 70),
            ('Shared', 100),
        ])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF', 'Shared': '#808080'}
        result = calculate_shared_split(df, partners, has_shared_partner=True)

        assert result['shared_total'] == 200.0
        assert result['per_person_share'] == 100.0
        assert result['grand_totals']['Alice'] == 200.0
        assert result['grand_totals']['Bob'] == 150.0


# =============================================
# Excel export tests
# =============================================

class TestGenerateExcel:
    def test_excel_without_shared_has_no_summary(self):
        """Without shared partner, Excel has only Expenses sheet."""
        df = make_expenses([('Alice', 100), ('Bob', 200)])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF'}
        excel_bytes = generate_excel(df, partners, has_shared_partner=False)

        sheets = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=None)
        assert 'Expenses' in sheets
        assert 'Summary' not in sheets

    def test_excel_with_shared_has_summary(self):
        """With shared partner, Excel has both Expenses and Summary sheets."""
        df = make_expenses([
            ('Alice', 100),
            ('Bob', 200),
            ('Shared', 60),
        ])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF', 'Shared': '#808080'}
        excel_bytes = generate_excel(df, partners, has_shared_partner=True)

        sheets = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=None)
        assert 'Expenses' in sheets
        assert 'Summary' in sheets

    def test_summary_sheet_values(self):
        """Summary sheet contains correct per-partner breakdown."""
        df = make_expenses([
            ('Alice', 100),
            ('Bob', 200),
            ('Shared', 60),
        ])
        partners = {'Alice': '#FF0000', 'Bob': '#0000FF', 'Shared': '#808080'}
        excel_bytes = generate_excel(df, partners, has_shared_partner=True)

        summary = pd.read_excel(io.BytesIO(excel_bytes), sheet_name='Summary')

        # Should have 3 rows: Alice, Bob, Shared Total
        assert len(summary) == 3
        alice_row = summary[summary['Partner'] == 'Alice'].iloc[0]
        assert alice_row['Own Total'] == 100.0
        assert alice_row['Share of Shared'] == 30.0
        assert alice_row['Grand Total'] == 130.0

        bob_row = summary[summary['Partner'] == 'Bob'].iloc[0]
        assert bob_row['Own Total'] == 200.0
        assert bob_row['Grand Total'] == 230.0

        shared_row = summary[summary['Partner'] == 'Shared Total'].iloc[0]
        assert shared_row['Own Total'] == 60.0

    def test_expenses_sheet_includes_shared_rows(self):
        """Raw Expenses sheet retains Shared rows as-is."""
        df = make_expenses([
            ('Alice', 100),
            ('Shared', 60),
        ])
        partners = {'Alice': '#FF0000', 'Shared': '#808080'}
        excel_bytes = generate_excel(df, partners, has_shared_partner=True)

        expenses = pd.read_excel(io.BytesIO(excel_bytes), sheet_name='Expenses')
        assert 'Shared' in expenses['Partner'].values
        assert len(expenses) == 2


# =============================================
# Streamlit integration tests
# =============================================

class TestStreamlitIntegration:
    """Tests that use streamlit.testing.v1 to verify UI flow."""

    @pytest.fixture(autouse=True)
    def _check_streamlit_testing(self):
        """Skip these tests if streamlit.testing is not available."""
        try:
            from streamlit.testing.v1 import AppTest
            self.AppTest = AppTest
        except ImportError:
            pytest.skip("streamlit.testing.v1 not available")

    def test_shared_toggle_adds_shared_partner(self):
        """Enabling shared toggle and confirming adds 'Shared' to partners."""
        at = self.AppTest.from_file("setup_page_harness.py", default_timeout=10)
        at.run()

        # Enable shared toggle
        at.toggle(key="shared_toggle").set_value(True).run()

        # Click Confirm Partners
        at.button[0].click().run()

        assert 'Shared' in at.session_state.partners
        assert at.session_state.partners['Shared'] == '#808080'
        assert at.session_state.has_shared_partner is True

    def test_shared_toggle_off_no_shared_partner(self):
        """Disabling shared toggle means no Shared partner."""
        at = self.AppTest.from_file("setup_page_harness.py", default_timeout=10)
        at.run()

        # Leave toggle off (default), click Confirm
        at.button[0].click().run()

        assert 'Shared' not in at.session_state.partners
        assert at.session_state.has_shared_partner is False


# =============================================
# Category rules matching tests
# =============================================

class TestCategoryRulesMatching:
    """Pure-Python tests for the keyword→category matching algorithm."""

    @staticmethod
    def match(rules, description):
        """Replicate the matching logic from app.py Focus Mode."""
        desc_lower = str(description).strip().lower()
        matched_category = None
        best_match_len = 0
        for keyword, kw_category in rules.items():
            if keyword in desc_lower and len(keyword) > best_match_len:
                matched_category = kw_category
                best_match_len = len(keyword)
        return matched_category

    def test_exact_match(self):
        rules = {"grocery store": "Groceries"}
        assert self.match(rules, "grocery store") == "Groceries"

    def test_case_insensitive(self):
        rules = {"grocery store": "Groceries"}
        assert self.match(rules, "GROCERY STORE") == "Groceries"

    def test_no_match_returns_none(self):
        rules = {"grocery store": "Groceries"}
        assert self.match(rules, "gas station") is None

    def test_longer_keyword_wins(self):
        rules = {
            "electric": "Utilities",
            "electric company payment": "Electricity",
        }
        assert self.match(rules, "electric company payment march") == "Electricity"

    def test_empty_rules(self):
        assert self.match({}, "anything at all") is None

    def test_substring_match(self):
        rules = {"walmart": "Groceries"}
        assert self.match(rules, "WALMART SUPERCENTER #1234") == "Groceries"

    def test_multiple_matches_longest_wins(self):
        rules = {
            "shell": "Fuel",
            "shell gas": "Fuel",
            "shell gas station": "Fuel & Auto",
        }
        assert self.match(rules, "shell gas station highway 101") == "Fuel & Auto"
