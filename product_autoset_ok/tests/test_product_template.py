# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductAutosetOk(TransactionCase):
    """test autoset of sale_ok and purchase_ok flags"""

    def setUp(self):
        """set up partners used by sale and purchase orders"""
        super().setUp()
        self.customer = self.env["res.partner"].create({"name": "Autoset Customer"})
        self.vendor = self.env["res.partner"].create({"name": "Autoset Vendor"})

    def _create_product(self, name):
        """create a product with both flags disabled"""
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "consu",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )

    def _create_sale_line(self, product):
        """create a sale order line for a product"""
        self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.display_name,
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                            "product_uom": product.uom_id.id,
                        }
                    )
                ],
            }
        )

    def _create_purchase_line(self, product):
        """create a purchase order line for a product"""
        self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.display_name,
                            "product_id": product.id,
                            "product_qty": 1.0,
                            "price_unit": 100.0,
                            "date_planned": "2026-03-05 00:00:00",
                            "product_uom": product.uom_po_id.id,
                        }
                    )
                ],
            }
        )

    def test_01_autoset_ok_sets_flags_for_used_products(self):
        """set sale_ok and purchase_ok only for products used in related lines"""
        used_sale_product = self._create_product("Used in Sale")
        used_purchase_product = self._create_product("Used in Purchase")
        unused_product = self._create_product("Unused Product")
        self._create_sale_line(used_sale_product)
        self._create_purchase_line(used_purchase_product)
        self.env["product.template"].autoset_ok()
        used_sale_product.product_tmpl_id.invalidate_recordset(
            ["sale_ok", "purchase_ok"]
        )
        used_purchase_product.product_tmpl_id.invalidate_recordset(
            ["sale_ok", "purchase_ok"]
        )
        unused_product.product_tmpl_id.invalidate_recordset(["sale_ok", "purchase_ok"])
        self.assertTrue(used_sale_product.product_tmpl_id.sale_ok)
        self.assertFalse(used_sale_product.product_tmpl_id.purchase_ok)
        self.assertTrue(used_purchase_product.product_tmpl_id.purchase_ok)
        self.assertFalse(used_purchase_product.product_tmpl_id.sale_ok)
        self.assertFalse(unused_product.product_tmpl_id.sale_ok)
        self.assertFalse(unused_product.product_tmpl_id.purchase_ok)

    def test_02_autoset_ok_updates_archived_products(self):
        """also set flags on archived templates because active_test is disabled"""
        archived_product = self._create_product("Archived Product")
        self._create_sale_line(archived_product)
        archived_product.product_tmpl_id.active = False
        self.env["product.template"].autoset_ok()
        archived_tmpl = (
            self.env["product.template"]
            .with_context(active_test=False)
            .browse(archived_product.product_tmpl_id.id)
        )
        archived_tmpl.invalidate_recordset(["sale_ok"])
        self.assertTrue(archived_tmpl.sale_ok)

    def test_03_autoset_ok_noop_when_no_lines(self):
        """keep flags unchanged when no sale or purchase lines exist"""
        product = self._create_product("No Lines Product")
        self.env["product.template"].autoset_ok()
        product.product_tmpl_id.invalidate_recordset(["sale_ok", "purchase_ok"])
        self.assertFalse(product.product_tmpl_id.sale_ok)
        self.assertFalse(product.product_tmpl_id.purchase_ok)
