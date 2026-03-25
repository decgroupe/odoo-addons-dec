# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestDocumentPageReferenceAuto(TransactionCase):
    """Test the automatic generation of document page references."""

    @classmethod
    def setUpClass(cls):
        """Set up a document.page record for use in tests."""
        super().setUpClass()
        cls.DocumentPage = cls.env["document.page"]

    def _simulate_onchange_name(self, name, existing_reference=""):
        """Create a new-style record, set name and reference, then trigger onchange."""
        page = self.DocumentPage.new({"name": name, "reference": existing_reference})
        page._onchange_name()
        return page.reference

    def test_01_simple_two_words(self):
        """words separated by spaces produce one letter each."""
        ref = self._simulate_onchange_name("Hello World")
        self.assertEqual(ref, "page_hw")

    def test_02_single_word(self):
        """a single word produces one letter."""
        ref = self._simulate_onchange_name("Installation")
        self.assertEqual(ref, "page_i")

    def test_03_split_on_comma(self):
        """commas are treated as separators."""
        ref = self._simulate_onchange_name("A,B,C")
        self.assertEqual(ref, "page_abc")

    def test_04_split_on_apostrophe(self):
        """apostrophes are treated as separators."""
        ref = self._simulate_onchange_name("Don't forget")
        self.assertEqual(ref, "page_dtf")

    def test_05_leading_digits_skipped(self):
        """parts that start with digits are skipped until a letter is found."""
        ref = self._simulate_onchange_name("123 Test")
        self.assertEqual(ref, "page_t")

    def test_06_pure_digit_part_ignored(self):
        """parts made entirely of digits contribute no letter."""
        ref = self._simulate_onchange_name("Section 1 Overview")
        self.assertEqual(ref, "page_so")

    def test_07_mixed_case_lowercased(self):
        """uppercase letters are lowercased in the resulting reference."""
        ref = self._simulate_onchange_name("My Document Page")
        self.assertEqual(ref, "page_mdp")

    def test_08_existing_reference_not_overwritten(self):
        """when a reference already exists the onchange must not change it."""
        ref = self._simulate_onchange_name(
            "Hello World", existing_reference="page_existing"
        )
        self.assertEqual(ref, "page_existing")

    def test_09_empty_name_no_reference_set(self):
        """an empty name must not generate a reference."""
        ref = self._simulate_onchange_name("")
        self.assertEqual(ref, "")

    def test_10_multiple_spaces_between_words(self):
        """extra spaces produce empty parts that contribute no letter."""
        ref = self._simulate_onchange_name("My  Document")
        self.assertEqual(ref, "page_md")

    def test_11_name_with_special_chars(self):
        """special characters that are not ascii letters are skipped within a part."""
        ref = self._simulate_onchange_name("3D Design Guide")
        self.assertEqual(ref, "page_ddg")
