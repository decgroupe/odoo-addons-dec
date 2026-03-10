# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026


from odoo import Command

from odoo.addons.stock_traceability.tests.common import TestStockTraceabilityBase


class TestStockTraceabilityMrpBase(TestStockTraceabilityBase):
    """Base class for tests for Stock Traceability module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.warehouse1 = self.env.ref("stock.warehouse0")
        self.route_mto = self.warehouse1.mto_pull_id.route_id
        self.route_mto.active = True
        self.route_manufacture = self.warehouse1.manufacture_pull_id.route_id
        # create a manufacturable product with a BoM to test the mrp status of moves
        self.manufacturable_product = self.env["product.product"].create(
            {
                "name": "Manufacturable Product",
                "type": "consu",
                "is_storable": True,
                "route_ids": [
                    Command.set([self.route_mto.id, self.route_manufacture.id])
                ],
            }
        )
        # create a BoM for the manufacturable product
        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.manufacturable_product.product_tmpl_id.id,
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "bom_line_ids": [
                    Command.create({"product_id": self.product.id, "product_qty": 1})
                ],
            }
        )
