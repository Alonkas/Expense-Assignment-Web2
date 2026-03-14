import pandas as pd
import pytest
from utils import auto_detect_columns, apply_mapping, load_excel, SHARED_KEYWORDS


class TestAutoDetectColumns:
    def test_english_columns(self):
        df = pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category'])
        result = auto_detect_columns(df)
        assert result['date'] == 'Date'
        assert result['desc'] == 'Description'
        assert result['amt'] == 'Amount'
        assert result['cat'] == 'Category'
        assert result['partner'] == "None"

    def test_hebrew_columns(self):
        df = pd.DataFrame(columns=['תאריך', 'תיאור', 'סכום', 'הערות'])
        result = auto_detect_columns(df)
        assert result['date'] == 'תאריך'
        assert result['desc'] == 'תיאור'
        assert result['amt'] == 'סכום'
        assert result['comment'] == 'הערות'

    def test_no_match(self):
        df = pd.DataFrame(columns=['Col1', 'Col2', 'Col3'])
        result = auto_detect_columns(df)
        assert result['date'] is None
        assert result['desc'] is None
        assert result['amt'] is None
        assert result['source'] == "None"
        assert result['partner'] == "None"

    def test_partial_match(self):
        df = pd.DataFrame(columns=['Transaction Date', 'Details', 'Total Amount'])
        result = auto_detect_columns(df)
        assert result['date'] == 'Transaction Date'
        assert result['amt'] == 'Total Amount'
        # 'Details' doesn't match any keyword
        assert result['desc'] is None

    def test_no_duplicate_assignment(self):
        """Each source column should only be assigned to one field."""
        df = pd.DataFrame(columns=['Date', 'Amount', 'Notes'])
        result = auto_detect_columns(df)
        assigned = [v for v in result.values() if v and v != "None"]
        assert len(assigned) == len(set(assigned))


class TestApplyMapping:
    def test_basic_mapping(self):
        df = pd.DataFrame({
            'MyDate': ['01/01/2024'],
            'MyDesc': ['Groceries'],
            'MyAmt': [50.0],
        })
        mapping = {
            'date': 'MyDate', 'desc': 'MyDesc', 'amt': 'MyAmt',
            'source': 'None', 'partner': 'None', 'cat': 'None', 'comment': 'None'
        }
        result = apply_mapping(df.copy(), mapping)
        assert list(result.columns[:7]) == ['Source', 'Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment']
        assert result.iloc[0]['Description'] == 'Groceries'
        assert result.iloc[0]['Amount'] == 50.0

    def test_optional_columns_filled(self):
        df = pd.DataFrame({
            'D': ['01/01/2024'], 'Desc': ['Test'], 'A': [10],
        })
        mapping = {
            'date': 'D', 'desc': 'Desc', 'amt': 'A',
            'source': 'None', 'partner': 'None', 'cat': 'None', 'comment': 'None'
        }
        result = apply_mapping(df.copy(), mapping)
        assert result.iloc[0]['Category'] == 'Uncategorized'
        assert result.iloc[0]['Comment'] == ''
        assert result.iloc[0]['Verified'] == False

    def test_matches_load_excel(self, tmp_path):
        """apply_mapping on a read DataFrame should match load_excel output."""
        df = pd.DataFrame({
            'Date': ['15/03/2024', '16/03/2024'],
            'Description': ['Coffee', 'Lunch'],
            'Amount': [12.5, 35.0],
            'Category': ['Dining', 'Dining'],
        })
        filepath = tmp_path / "test.xlsx"
        df.to_excel(filepath, index=False)

        mapping = {
            'date': 'Date', 'desc': 'Description', 'amt': 'Amount',
            'source': 'None', 'partner': 'None', 'cat': 'Category', 'comment': 'None'
        }
        from_load = load_excel(str(filepath), mapping)
        raw = pd.read_excel(filepath)
        from_apply = apply_mapping(raw, mapping)

        pd.testing.assert_frame_equal(from_load, from_apply)


class TestSharedKeywordDetection:
    def test_shared_english(self):
        partners = ['Alice', 'Bob', 'Shared']
        has_shared = any(p.lower() in SHARED_KEYWORDS for p in partners)
        assert has_shared is True

    def test_shared_hebrew(self):
        partners = ['Alice', 'משותף']
        has_shared = any(p.lower() in SHARED_KEYWORDS for p in partners)
        assert has_shared is True

    def test_no_shared(self):
        partners = ['Alice', 'Bob']
        has_shared = any(p.lower() in SHARED_KEYWORDS for p in partners)
        assert has_shared is False

    def test_common_keyword(self):
        partners = ['Alice', 'Common']
        has_shared = any(p.lower() in SHARED_KEYWORDS for p in partners)
        assert has_shared is True
