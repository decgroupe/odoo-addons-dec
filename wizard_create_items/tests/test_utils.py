# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2025


from odoo.tests.common import BaseCase

from ..utils import (
    _deduplicate,
    _detect_separator,
    _extract_items_from_html,
    _extract_items_from_list,
    _extract_items_from_plaintext,
    _extract_items_from_table,
    _parse_items_with_separator,
)


class TestUtils(BaseCase):
    def setUp(self):
        super().setUp()

    def test_01_extract_items_from_html_list(self):
        """Test extraction from HTML list with <li> tags"""
        html = """
        <ul>
            <li>Item One</li>
            <li>Item Two</li>
            <li>Item Three</li>
        </ul>
        """
        result, _separator = _extract_items_from_html(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("", "Item One"))
        self.assertEqual(result[1], ("", "Item Two"))
        self.assertEqual(result[2], ("", "Item Three"))

    def test_02_extract_items_from_dash_list(self):
        """Test extraction from dash-prefixed list"""
        html = """
        - Item One
        - Item Two
        - Item Three
        -
        Item Five
        """
        result, _separator = _extract_items_from_html(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("", "Item One"))
        self.assertEqual(result[1], ("", "Item Two"))
        self.assertEqual(result[2], ("", "Item Three"))

    def test_03_extract_items_from_plain_lines(self):
        """Test extraction from plain lines"""
        html = """
        Item One
        Item Two
        Item Three
        """
        result, _separator = _extract_items_from_html(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("", "Item One"))
        self.assertEqual(result[1], ("", "Item Two"))
        self.assertEqual(result[2], ("", "Item Three"))

    def test_10_extract_items_from_table(self):
        """Test extraction from HTML table"""
        html = """
        <table>
            <tr>
                <td>TM1</td>
                <td>Reading Comprehension</td>
            </tr>
            <tr>
                <td>TM2</td>
                <td>Writing Exercise</td>
            </tr>
            <tr>
                <td>TM4</td>
                <td>Listening Practice</td>
            </tr>
        </table>
        """
        result = _extract_items_from_table(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("TM1", "Reading Comprehension"))
        self.assertEqual(result[1], ("TM2", "Writing Exercise"))
        self.assertEqual(result[2], ("TM4", "Listening Practice"))

    def test_11_extract_items_from_table_via_main_function(self):
        """Test that main function uses table parsing"""
        html = """
        <table>
            <tr>
                <td>TM1</td>
                <td>First Item</td>
            </tr>
            <tr>
                <td>TM2</td>
                <td>Second Item</td>
            </tr>
        </table>
        """
        result, _separator = _extract_items_from_html(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("TM1", "First Item"))
        self.assertEqual(result[1], ("TM2", "Second Item"))

    def test_12_extract_items_from_table_single_column(self):
        """Test extraction from HTML table with single column"""
        html = """
        <table>
            <tr>
                <td>Reading Comprehension</td>
            </tr>
            <tr>
                <td>Writing Exercise</td>
            </tr>
            <tr>
                <td>Listening Practice</td>
            </tr>
        </table>
        """
        result = _extract_items_from_table(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("", "Reading Comprehension"))
        self.assertEqual(result[1], ("", "Writing Exercise"))
        self.assertEqual(result[2], ("", "Listening Practice"))

    def test_13_extract_items_from_table_empty_code(self):
        """Test extraction from HTML table with empty first column"""
        html = """
        <table>
            <tr>
                <td></td>
                <td>Reading Comprehension</td>
            </tr>
            <tr>
                <td></td>
                <td>Writing Exercise</td>
            </tr>
            <tr>
                <td>TM4</td>
                <td>Listening Practice</td>
            </tr>
        </table>
        """
        result = _extract_items_from_table(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("", "Reading Comprehension"))
        self.assertEqual(result[1], ("", "Writing Exercise"))
        self.assertEqual(result[2], ("TM4", "Listening Practice"))

    def test_20_extract_items_deduplication(self):
        """Test that duplicates are removed"""
        html = """
        <ul>
            <li>Item One</li>
            <li>Item Two</li>
            <li>Item One</li>
        </ul>
        """
        result, _separator = _extract_items_from_html(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("", "Item One"))
        self.assertEqual(result[1], ("", "Item Two"))

    def test_30_detect_separator_colon(self):
        """Test separator detection with colon"""
        items = [
            "ID1: Name One",
            "ID2: Name Two",
            "ID3: Name Three",
        ]
        separator = _detect_separator(items)
        self.assertEqual(separator, ":")

    def test_31_detect_separator_equals(self):
        """Test separator detection with equals"""
        items = [
            "ID1=Name One",
            "ID2=Name Two",
            "ID3=Name Three",
        ]
        separator = _detect_separator(items)
        self.assertEqual(separator, "=")

    def test_32_detect_separator_dash(self):
        """Test separator detection with dash"""
        items = [
            "ID1 - Name One",
            "ID2 - Name Two",
            "ID3 - Name Three",
        ]
        separator = _detect_separator(items)
        self.assertEqual(separator, " - ")

    def test_33_detect_separator_triple_dash(self):
        """Test separator detection with triple dash"""
        items = [
            "ID1---Name One",
            "ID2---Name Two",
            "ID3---Name Three",
        ]
        separator = _detect_separator(items)
        self.assertEqual(separator, "---")

    def test_34_detect_separator_pipe(self):
        """Test separator detection with pipe"""
        items = [
            "ID1|Name One",
            "ID2|Name Two",
            "ID3|Name Three",
        ]
        separator = _detect_separator(items)
        self.assertEqual(separator, "|")

    def test_35_detect_separator_no_pattern(self):
        """Test separator detection with no consistent pattern"""
        items = [
            "ID1 Name One",
            "ID2 Name Two",
            "ID3 Name Three",
        ]
        separator = _detect_separator(items)
        self.assertIsNone(separator)

    def test_36_detect_separator_partial_match(self):
        """Test separator detection with partial match (below threshold)"""
        items = ["ID1: Name One", "Name Two", "Name Three", "Name Four"]
        separator = _detect_separator(items)
        # Only 1 out of 4 items has ":", should be None
        self.assertIsNone(separator)

    def test_37_detect_separator_threshold_2_items(self):
        """Test separator detection with 2 items (30% threshold)"""
        items = ["ID1: Name One", "Name Two"]
        separator = _detect_separator(items)
        # 1 out of 2 items = 50%, threshold is 30%
        self.assertEqual(separator, ":")

    def test_38_detect_separator_threshold_3_items(self):
        """Test separator detection with 3 items (40% threshold)"""
        items = [
            "ID1: Name One",
            "ID2: Name Two",
            "Name Three",
        ]
        separator = _detect_separator(items)
        # 2 out of 3 items = 66%, threshold is 40%
        self.assertEqual(separator, ":")

    def test_39_detect_separator_empty_list(self):
        """Test separator detection with empty list"""
        items = []
        separator = _detect_separator(items)
        self.assertIsNone(separator)

    def test_40_detect_separator_single_item(self):
        """Test separator detection with single item"""
        items = ["ID1: Name One"]
        separator = _detect_separator(items)
        # With 1 item, probability threshold is 0, should not detect
        self.assertIsNone(separator)

    def test_41_parse_items_with_separator_colon(self):
        """Test parsing items with colon separator"""
        items = ["ID1: Name One", "ID2: Name Two"]
        result, separator = _parse_items_with_separator(items)
        self.assertEqual(separator, ":")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("ID1", "Name One"))
        self.assertEqual(result[1], ("ID2", "Name Two"))

    def test_42_parse_items_with_separator_custom(self):
        """Test parsing items with custom separator"""
        items = ["ID1=>Name One", "ID2=>Name Two"]
        result, separator = _parse_items_with_separator(items, separator="=>")
        self.assertEqual(separator, "=>")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("ID1", "Name One"))
        self.assertEqual(result[1], ("ID2", "Name Two"))

    def test_43_parse_items_without_separator(self):
        """Test parsing items without separator"""
        items = [
            "Name One",
            "Name Two",
            "Name Three",
        ]
        result, separator = _parse_items_with_separator(items)
        self.assertIsNone(separator)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("", "Name One"))
        self.assertEqual(result[1], ("", "Name Two"))

    def test_44_parse_items_mixed_separator(self):
        """Test parsing items where some have separator, some don't"""
        items = [
            "ID1: Name One",
            "Name Two",
            "ID3: Name Three",
        ]
        result, separator = _parse_items_with_separator(items)
        self.assertEqual(separator, ":")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("ID1", "Name One"))
        self.assertEqual(result[1], ("", "Name Two"))
        self.assertEqual(result[2], ("ID3", "Name Three"))

    def test_45_parse_items_empty_list(self):
        """Test parsing empty items list"""
        items = []
        result, separator = _parse_items_with_separator(items)
        self.assertEqual(result, [])
        self.assertIsNone(separator)

    def test_46_parse_items_with_deduplication(self):
        """Test that parsing deduplicates items"""
        items = ["ID1: Name", "ID2: Name", "ID1: Name"]
        result, _separator = _parse_items_with_separator(items)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("ID1", "Name"))
        self.assertEqual(result[1], ("ID2", "Name"))

    def test_50_extract_items_from_list_ordered(self):
        """Test extraction from ordered list"""
        html = """
        <ol>
            <li>First Item</li>
            <li>Second Item</li>
        </ol>
        """
        result = _extract_items_from_list(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "First Item")
        self.assertEqual(result[1], "Second Item")

    def test_51_extract_items_from_list_empty(self):
        """Test extraction from empty list"""
        html = "<ul></ul>"
        result = _extract_items_from_list(html)
        self.assertEqual(result, [])

    def test_52_extract_items_from_list_with_nested_tags(self):
        """Test extraction from list with nested tags"""
        html = """
        <ul>
            <li><strong>Bold</strong> Item</li>
            <li>Normal <em>Italic</em> Item</li>
        </ul>
        """
        result = _extract_items_from_list(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Bold Item")
        self.assertEqual(result[1], "Normal Italic Item")

    def test_53_extract_items_from_list_empty_li(self):
        """Test extraction from list with empty li elements"""
        html = """
        <ul>
            <li>Item One</li>
            <li></li>
            <li>Item Two</li>
        </ul>
        """
        result = _extract_items_from_list(html)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Item One")
        self.assertEqual(result[1], "Item Two")

    def test_60_extract_items_from_plaintext_dash_list(self):
        """Test extraction from plaintext with dash list"""
        html = "- Item One\n- Item Two\n- Item Three"
        result = _extract_items_from_plaintext(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "Item One")
        self.assertEqual(result[1], "Item Two")
        self.assertEqual(result[2], "Item Three")

    def test_61_extract_items_from_plaintext_regular_lines(self):
        """Test extraction from plaintext without dashes"""
        html = "Item One\nItem Two\nItem Three"
        result = _extract_items_from_plaintext(html)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "Item One")
        self.assertEqual(result[1], "Item Two")
        self.assertEqual(result[2], "Item Three")

    def test_62_extract_items_from_plaintext_empty(self):
        """Test extraction from empty plaintext"""
        html = ""
        result = _extract_items_from_plaintext(html)
        self.assertEqual(result, [])

    def test_63_extract_items_from_plaintext_html_tags(self):
        """Test extraction from plaintext with HTML tags"""
        html = "<p>Item One</p>\n<p>Item Two</p>"
        result = _extract_items_from_plaintext(html)
        # html2plaintext should strip tags
        self.assertGreater(len(result), 0)

    def test_70_extract_items_with_separator_in_html(self):
        """Test extraction with separator detection"""
        html = """
        <ul>
            <li>ID1: Name One</li>
            <li>ID2: Name Two</li>
            <li>ID3: Name Three</li>
        </ul>
        """
        result, separator = _extract_items_from_html(html)
        self.assertEqual(separator, ":")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("ID1", "Name One"))
        self.assertEqual(result[1], ("ID2", "Name Two"))
        self.assertEqual(result[2], ("ID3", "Name Three"))

    def test_71_extract_items_with_forced_separator(self):
        """Test extraction with forced separator"""
        html = """
        <ul>
            <li>ID1=>Name One</li>
            <li>ID2=>Name Two</li>
        </ul>
        """
        result, separator = _extract_items_from_html(html, separator="=>")
        self.assertEqual(separator, "=>")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("ID1", "Name One"))
        self.assertEqual(result[1], ("ID2", "Name Two"))

    def test_72_extract_items_empty_html(self):
        """Test extraction from empty HTML"""
        result, separator = _extract_items_from_html("")
        self.assertEqual(result, [])
        self.assertIsNone(separator)

    def test_73_extract_items_none_html(self):
        """Test extraction from None HTML"""
        result, separator = _extract_items_from_html(None)
        self.assertEqual(result, [])
        self.assertIsNone(separator)

    def test_80_deduplicate_function(self):
        """Test _deduplicate function"""
        items = [("A", "1"), ("B", "2"), ("A", "1"), ("C", "3")]
        result = _deduplicate(items)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("A", "1"))
        self.assertEqual(result[1], ("B", "2"))
        self.assertEqual(result[2], ("C", "3"))

    def test_81_deduplicate_preserves_order(self):
        """Test that _deduplicate preserves order"""
        items = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        result = _deduplicate(items)
        self.assertEqual(result, [3, 1, 4, 5, 9, 2, 6])

    def test_90_extract_items_from_table_with_header(self):
        """Test extraction from table with header row"""
        html = """
        <table>
            <tr>
                <th>Code</th>
                <th>Name</th>
            </tr>
            <tr>
                <td>A1</td>
                <td>Item One</td>
            </tr>
        </table>
        """
        result = _extract_items_from_table(html)
        # Headers should be included as they use th tags
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("Code", "Name"))
        self.assertEqual(result[1], ("A1", "Item One"))

    def test_91_extract_items_from_table_empty(self):
        """Test extraction from empty table"""
        html = "<table></table>"
        result = _extract_items_from_table(html)
        self.assertEqual(result, [])
