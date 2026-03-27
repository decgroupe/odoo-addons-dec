# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestStockOrderpointIgnore(TransactionCase):
    """Tests for stock_orderpoint_ignore module.

    Verifies that _run_buy skips procurements triggered by orderpoints when
    the product's procurement method is 'make_to_order', while still processing
    procurements for 'make_to_stock' products or procurements without an
    orderpoint.
    """

    @classmethod
    def setUpClass(cls):
        """Set up common test data: warehouse, routes, partner, products and
        orderpoints."""
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.route_mto = cls.warehouse.mto_pull_id.route_id
        cls.route_buy = cls.warehouse.buy_pull_id.route_id
        # enable MTO route (archived by default in Odoo)
        cls.route_mto.active = True
        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier"})
        # product_mto has both MTO and Buy routes → procure_method = 'make_to_order'
        cls.product_mto = cls.env["product.product"].create(
            {
                "name": "MTO Product",
                "type": "consu",
                "is_storable": True,
                "route_ids": [
                    Command.link(cls.route_mto.id),
                    Command.link(cls.route_buy.id),
                ],
                "seller_ids": [Command.create({"partner_id": cls.partner.id})],
            }
        )
        # product_mts has only Buy route → procure_method = 'make_to_stock'
        cls.product_mts = cls.env["product.product"].create(
            {
                "name": "MTS Product",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.link(cls.route_buy.id)],
                "seller_ids": [Command.create({"partner_id": cls.partner.id})],
            }
        )
        cls.location = cls.warehouse.lot_stock_id
        cls.orderpoint_mto = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.product_mto.id,
                "location_id": cls.location.id,
                "product_min_qty": 5.0,
                "product_max_qty": 10.0,
            }
        )
        cls.orderpoint_mts = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.product_mts.id,
                "location_id": cls.location.id,
                "product_min_qty": 5.0,
                "product_max_qty": 10.0,
            }
        )
        # use the warehouse buy rule directly to isolate tests from route resolution
        cls.buy_rule = cls.warehouse.buy_pull_id
        cls.procurement_group = cls.env["procurement.group"].create({"name": "Test PG"})

    def _build_procurement(self, product, qty, orderpoint=None):
        """Build a Procurement namedtuple for direct use with _run_buy."""
        values = {
            "warehouse_id": self.warehouse,
            "group_id": self.procurement_group,
            "date_planned": fields.Datetime.now(),
        }
        if orderpoint:
            values["orderpoint_id"] = orderpoint
        return self.env["procurement.group"].Procurement(
            product,
            qty,
            product.uom_id,
            self.location,
            product.display_name,
            "/",
            self.env.company,
            values,
        )

    def _get_purchase_orders(self, product):
        """Return purchase orders for the given product and test partner."""
        return self.env["purchase.order"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("order_line.product_id", "=", product.id),
            ]
        )

    def test_01_mto_product_with_orderpoint_is_ignored(self):
        """A procurement with orderpoint_id for a `make_to_order` product must be
        ignored."""
        self.assertEqual(self.product_mto.procure_method, "make_to_order")
        procurement = self._build_procurement(
            self.product_mto, 5.0, orderpoint=self.orderpoint_mto
        )
        self.env["stock.rule"]._run_buy([(procurement, self.buy_rule)])
        po = self._get_purchase_orders(self.product_mto)
        self.assertFalse(
            po,
            "No purchase order should be created for a `make_to_order` "
            "product triggered by an orderpoint",
        )

    def test_02_mts_product_with_orderpoint_is_processed(self):
        """A procurement with orderpoint_id for a `make_to_stock` product must
        create a PO."""
        self.assertEqual(self.product_mts.procure_method, "make_to_stock")
        procurement = self._build_procurement(
            self.product_mts, 5.0, orderpoint=self.orderpoint_mts
        )
        self.env["stock.rule"]._run_buy([(procurement, self.buy_rule)])
        po = self._get_purchase_orders(self.product_mts)
        self.assertTrue(
            po,
            "A purchase order should be created for a `make_to_stock` "
            "product triggered by an orderpoint",
        )

    def test_03_mto_product_without_orderpoint_is_processed(self):
        """A procurement without orderpoint_id for a `make_to_order` product must
        create a PO."""
        self.assertEqual(self.product_mto.procure_method, "make_to_order")
        procurement = self._build_procurement(self.product_mto, 5.0, orderpoint=None)
        self.env["stock.rule"]._run_buy([(procurement, self.buy_rule)])
        po = self._get_purchase_orders(self.product_mto)
        self.assertTrue(
            po,
            "A purchase order should be created for a `make_to_order` "
            "product when there is no orderpoint",
        )
