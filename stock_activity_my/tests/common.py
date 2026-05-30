# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from lxml import etree

from odoo.tests.common import TransactionCase


class TestStockActivityMyCommon(TransactionCase):
    """Shared helpers for stock_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()

    def _get_view_arch(self, model_name, view_type="list", view_xmlid=None):
        """Return parsed combined view architecture for assertions."""
        view_id = self.env.ref(view_xmlid).id if view_xmlid else None
        view_info = self.env[model_name].get_view(view_id=view_id, view_type=view_type)
        return etree.fromstring(view_info["arch"].encode())
