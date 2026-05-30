# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from .common import TestStockActivityMyCommon


class TestStockActivityMy(TestStockActivityMyCommon):
    """Tests for stock_activity_my module."""

    def test_01_picking_list_has_remaining_days_widget(self):
        """Check that scheduled_date uses remaining_days widget in list view."""
        arch = self._get_view_arch(
            model_name="stock.picking",
            view_type="list",
            view_xmlid="stock_activity_my.vpicktree",
        )
        scheduled_date_nodes = arch.xpath("//field[@name='scheduled_date']")
        self.assertTrue(scheduled_date_nodes)
        self.assertEqual(scheduled_date_nodes[0].get("widget"), "remaining_days")

    def test_02_picking_list_keeps_name_decoration(self):
        """Check that name field keeps the expected bold decoration."""
        arch = self._get_view_arch(
            model_name="stock.picking",
            view_type="list",
            view_xmlid="stock_activity_my.vpicktree",
        )
        name_nodes = arch.xpath("//field[@name='name']")
        self.assertTrue(name_nodes)
        self.assertEqual(name_nodes[0].get("decoration-bf"), "1")
