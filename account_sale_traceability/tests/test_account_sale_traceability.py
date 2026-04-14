# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from odoo import Command

from .common import TestAccountSaleTraceabilityCommon


class TestAccountSaleTraceability(TestAccountSaleTraceabilityCommon):
    """Tests for account_sale_traceability module."""

    def test_01_invoice_origin_propagated_to_move_line(self):
        """Check that invoice_origin is stored on move lines via related field."""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "invoice_origin": "SO001",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "account_id": self.sale_account.id,
                        }
                    )
                ],
            }
        )
        invoice_lines = invoice.invoice_line_ids
        self.assertTrue(invoice_lines)
        for line in invoice_lines:
            self.assertEqual(line.invoice_origin, "SO001")

    def test_02_invoice_origin_updated_when_move_changes(self):
        """Check that stored invoice_origin is updated when move origin changes."""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.journal.id,
                "invoice_origin": "SO001",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "account_id": self.sale_account.id,
                        }
                    )
                ],
            }
        )
        invoice.invoice_origin = "SO002"
        invoice.invalidate_recordset()
        invoice_lines = invoice.invoice_line_ids
        self.assertTrue(invoice_lines)
        for line in invoice_lines:
            self.assertEqual(line.invoice_origin, "SO002")

    def test_03_move_line_form_view_fields(self):
        """Check that sale_line_ids field is present in combined form view arch."""
        view_info = self.env["account.move.line"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("sale_line_ids", field_names)

    def test_04_move_line_search_view_fields(self):
        """Check that invoice_origin field is present in combined search view arch."""
        view_info = self.env["account.move.line"].get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("invoice_origin", field_names)

    def test_05_move_list_view_fields(self):
        """Check that invoice_origin field is present in combined list view arch."""
        view_info = self.env["account.move"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("invoice_origin", field_names)

    def test_06_move_search_view_fields(self):
        """Check that invoice_origin field is in the journal entries
        search view arch."""
        # target the specific view our module extends (journal entries filter)
        view = self.env.ref("account_sale_traceability.account_move_filter_view")
        view_info = self.env["account.move"].get_view(
            view_id=view.id, view_type="search"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("invoice_origin", field_names)
