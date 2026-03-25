# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchaseSupplier(TransactionCase):
    """Test the purchase supplier module which adds the possibility to select a
    supplier on a BoM line, and have it taken into account when generating procurements
    from a stock move linked to that BoM line."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Move = cls.env["stock.move"]
        cls.Product = cls.env["product.product"]
        cls.Bom = cls.env["mrp.bom"]
        cls.Production = cls.env["mrp.production"]
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def setUp(self):
        super().setUp()
        # create vendors
        self.vendor1 = self.env["res.partner"].create(
            {"name": "Test Vendor #1", "supplier_rank": 1}
        )
        self.vendor2 = self.env["res.partner"].create(
            {"name": "Test Vendor #2", "supplier_rank": 1}
        )
        # create a finished product
        self.finished_product = self.Product.create(
            {
                "name": "Finished Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # create a component with the vendor as seller
        self.component = self.Product.create(
            {
                "name": "Component",
                "type": "consu",
                "is_storable": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.vendor1.id,
                            "min_qty": 1.0,
                            "price": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "partner_id": self.vendor2.id,
                            "min_qty": 1.0,
                            "price": 20.0,
                        }
                    ),
                ],
            }
        )
        self.supplierinfo1 = self.component.seller_ids[0]
        self.supplierinfo2 = self.component.seller_ids[1]
        # create a bill of materials with the component
        self.bom = self.Bom.create(
            {
                "product_tmpl_id": self.finished_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": self.component.id,
                            "product_qty": 1.0,
                        }
                    )
                ],
            }
        )
        self.bom_line = self.bom.bom_line_ids[0]
        self.src_location = self.warehouse.lot_stock_id
        self.dest_location = self.env.ref("stock.stock_location_customers")

    def _make_move(self, bom_line=None):
        """create a stock.move for the component, optionally linked to a bom line."""
        vals = {
            "name": "Test Move",
            "location_id": self.src_location.id,
            "location_dest_id": self.dest_location.id,
            "product_id": self.component.id,
            "product_uom": self.component.uom_id.id,
            "product_uom_qty": 1.0,
        }
        if bom_line:
            vals["bom_line_id"] = bom_line.id
        return self.Move.create(vals)

    def test_01_without_bom_line(self):
        """_prepare_procurement_values should not add supplierinfo_id
        when the move has no bom_line_id set."""
        move = self._make_move()
        result = move._prepare_procurement_values()
        self.assertNotIn("supplierinfo_id", result)

    def test_02_bom_line_without_partner(self):
        """_prepare_procurement_values should not add supplierinfo_id
        when the bom line has no partner_id (no specific supplier chosen)."""
        move = self._make_move(bom_line=self.bom_line)
        self.assertFalse(self.bom_line.partner_id)
        result = move._prepare_procurement_values()
        self.assertNotIn("supplierinfo_id", result)

    def test_03_bom_line_with_partner(self):
        """_prepare_procurement_values should include supplierinfo_id matching
        the seller derived from the bom line's partner_id."""
        self.bom_line.partner_id = self.vendor2
        move = self._make_move(bom_line=self.bom_line)
        self.assertTrue(self.bom_line.seller_id)
        result = move._prepare_procurement_values()
        self.assertIn("supplierinfo_id", result)
        self.assertEqual(result["supplierinfo_id"], self.bom_line.seller_id)
        self.assertEqual(result["supplierinfo_id"], self.supplierinfo2)

    def test_04_workflow_purchase_order_per_vendor(self):
        """Confirm that confirming a production order creates a PO for the right vendor.
        When the BoM line has a partner_id set, the generated PO should be for that
        partner. Changing the BoM line partner and confirming a new production order
        should create a PO for the new partner."""
        # activate MTO route and assign MTO+buy routes to the component
        route_mto = self.warehouse.mto_pull_id.route_id
        route_buy = self.warehouse.buy_pull_id.route_id
        route_mto.active = True
        self.component.route_ids = [Command.set(route_buy.ids + route_mto.ids)]
        # set bom line partner to vendor1 so procurements will use vendor1 supplierinfo
        self.bom_line.partner_id = self.vendor1
        # check that no purchase orders exist for vendor1
        self.assertFalse(
            self.PurchaseOrder.search([("partner_id", "=", self.vendor1.id)])
        )
        # create and confirm production order, the component move triggers procurement
        mo1 = self.Production.create(
            {
                "product_id": self.finished_product.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "product_uom_id": self.finished_product.uom_id.id,
            }
        )
        mo1.action_confirm()
        # check that a purchase order has been created for vendor1
        pos_vendor1 = self.PurchaseOrder.search([("partner_id", "=", self.vendor1.id)])
        self.assertTrue(pos_vendor1)
        # check that no purchase orders exist for vendor2
        self.assertFalse(
            self.PurchaseOrder.search([("partner_id", "=", self.vendor2.id)])
        )
        # change the bom line partner to vendor2
        self.bom_line.partner_id = self.vendor2
        # create and confirm a new production order
        mo2 = self.Production.create(
            {
                "product_id": self.finished_product.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "product_uom_id": self.finished_product.uom_id.id,
            }
        )
        mo2.action_confirm()
        # check that a purchase order has been created for vendor2
        pos_vendor2 = self.PurchaseOrder.search([("partner_id", "=", self.vendor2.id)])
        self.assertTrue(pos_vendor2)
