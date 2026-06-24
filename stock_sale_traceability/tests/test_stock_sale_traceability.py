# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from lxml import etree

import odoo
from odoo.tests.common import TransactionCase

from odoo.addons.website.tools import MockRequest


class TestStockSaleTraceability(TransactionCase):
    """Tests for stock_sale_traceability module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.ProcurementGroup = cls.env["procurement.group"]
        # create a minimal sale order so we can link it to a group
        partner = cls.env.ref("base.res_partner_1")
        product = cls.env["product.product"].search([("type", "=", "consu")], limit=1)
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        odoo.Command.create(
                            {
                                "product_id": product.id,
                                "product_uom_qty": 1,
                                "price_unit": 10,
                            }
                        ),
                    )
                ],
            }
        )

    def _make_group(self, name, sale_id=False):
        """Create a procurement.group with the given name and optional sale order."""
        vals = {"name": name}
        if sale_id:
            vals["sale_id"] = sale_id
        return self.ProcurementGroup.create(vals)

    def test_01_no_sale_order_uses_group_name(self):
        """get_head_desc returns the group name as desc when no sale order is linked."""
        group = self._make_group("GRP-001")
        head, desc = group.get_head_desc()
        self.assertEqual(head, "📋")
        self.assertEqual(desc, "GRP-001")

    def test_02_sale_order_name_different_from_group_name(self):
        """get_head_desc returns the sale order name as desc when it differs from the
        group name."""
        group = self._make_group("GRP-002", sale_id=self.sale_order.id)
        head, desc = group.get_head_desc()
        self.assertEqual(head, "📋")
        self.assertEqual(desc, self.sale_order.name)

    def test_03_sale_order_same_name_as_group_uses_group_name(self):
        """get_head_desc falls back to group name when sale order name equals group
        name."""
        group = self._make_group(self.sale_order.name, sale_id=self.sale_order.id)
        head, desc = group.get_head_desc()
        self.assertEqual(head, "📋")
        # names are equal so override must not apply
        self.assertEqual(desc, group.name)

    def test_04_sale_line_id_appears_once_in_stock_move_form_view(self):
        """sale_line_id field is present exactly once in the stock.move form view
        arch."""
        with MockRequest(self.env) as mock:
            # simulate a debug HTTP request so base.group_no_one is active
            mock.session.debug = True
            self.assertTrue(self.env.user.has_group("base.group_no_one"))
            view_info = self.env["stock.move"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        fields = arch.xpath("//field[@name='sale_line_id']")
        self.assertEqual(
            len(fields),
            1,
            "sale_line_id must appear exactly once in stock_move form view arch",
        )
