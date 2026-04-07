# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductFavoriteCommon(TransactionCase):
    """Base class with shared fixtures for product_favorite tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Favorite Customer"})
        cls.vendor = cls.env["res.partner"].create({"name": "Favorite Vendor"})
        cls.component_product = cls.env["product.product"].create(
            {
                "name": "Component Product",
                "type": "consu",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "type": "consu",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )
        cls.unused_product = cls.env["product.product"].create(
            {
                "name": "Unused Product",
                "type": "consu",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )

    def _create_sale_order(self, product):
        """Create a confirmed sale order with one line for the given product."""
        return self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.display_name,
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 10.0,
                            "product_uom": product.uom_id.id,
                        }
                    )
                ],
            }
        )

    def _create_purchase_order(self, product):
        """Create a purchase order with one line for the given product."""
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.display_name,
                            "product_id": product.id,
                            "product_qty": 1.0,
                            "price_unit": 10.0,
                            "date_planned": "2026-04-07 00:00:00",
                            "product_uom": product.uom_po_id.id,
                        }
                    )
                ],
            }
        )

    def _create_bom(self, finished_product, component_product):
        """Create a bill of materials with one component line."""
        return self.env["mrp.bom"].create(
            {
                "product_tmpl_id": finished_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": component_product.id,
                            "product_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def assertNameSearch(self, record, search_term, expected_name):
        """Assert name_search returns the expected display name for the record."""
        Model = self.env[record._name]
        Model.invalidate_model(["display_name"])
        res = Model.name_search(name=search_term)
        if not expected_name:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], record.id)
            self.assertEqual(res[0][1], expected_name)
        except IndexError:
            self.fail(
                f"Expected to find a record with name_search '{search_term}' "
                f"but found {res}.\n"
                f"Value is '{record.display_name}'"
            )

    def assertDisplayName(self, record, normal_name, name_search_name):
        return self._assertDisplayName(
            record,
            {"name_search": True},
            normal_name,
            name_search_name,
        )

    def _assertDisplayName(self, record, context, normal_name, name_search_name):
        """Assert plain display_name, then display_name with given context."""
        Model = self.env[record._name]
        Model.invalidate_model(["display_name"])
        self.assertEqual(record.display_name, normal_name)
        Model.invalidate_model(["display_name"])
        self.assertEqual(record.with_context(**context).display_name, name_search_name)
