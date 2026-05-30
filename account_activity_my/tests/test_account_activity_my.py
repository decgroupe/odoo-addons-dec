# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestAccountActivityMyCommon


class TestAccountActivityMy(TestAccountActivityMyCommon):
    """Tests for account_activity_my module."""

    def test_01_account_move_has_mixin_fields(self):
        """Check that account.move exposes mail.activity.my.mixin fields."""
        self.assertIn("activity_my_ids", self.AccountMove._fields)
        self.assertIn("activity_my_state", self.AccountMove._fields)
        self.assertIn("activity_my_date_deadline", self.AccountMove._fields)

    def test_02_invoice_list_view_fields(self):
        """Check the inherited invoice list view exposes activity_my_ids."""
        view_info = self.AccountMove.get_view(
            view_id=self.invoice_tree_view.id,
            view_type="list",
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
