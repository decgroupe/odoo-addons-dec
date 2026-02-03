# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026


from freezegun import freeze_time

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpBomSupplier(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Picking = cls.env["stock.picking"]
        cls.Move = cls.env["stock.move"]
        cls.Production = cls.env["mrp.production"]
        cls.Product = cls.env["product.product"]
        cls.Orderpoint = cls.env["stock.warehouse.orderpoint"]
        cls.StockLocation = cls.env["stock.location"]
        cls.Route = cls.env["stock.route"]
        cls.Bom = cls.env["mrp.bom"]
        cls.BomLine = cls.env["mrp.bom.line"]
        cls.PurchaseLine = cls.env["purchase.order.line"]
        cls.ProcurementGroup = cls.env["procurement.group"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.warehouse.in_type_id
        cls.picking_type_out = cls.warehouse.out_type_id

        cls.stock_loc = cls.warehouse.lot_stock_id

    def setUp(self):
        super().setUp()
        # create vendors
        self.vendor_1 = self.env["res.partner"].create(
            {"name": "Vendor 1", "supplier_rank": 1}
        )
        # prepare routes
        route_manuf = self.warehouse.manufacture_pull_id.route_id
        route_buy = self.warehouse.buy_pull_id.route_id
        route_mto = self.warehouse.mto_pull_id.route_id
        route_mto.active = True
        # prepare products
        self.product_to_manufacture = self.Product.create(
            {
                "name": "Test Product",
                "route_ids": [Command.set(route_manuf.ids)],
                "type": "consu",
                "is_storable": True,
            }
        )
        component_for_product = self.Product.create(
            {
                "name": "Test component",
                "route_ids": [Command.set(route_buy.ids + route_mto.ids)],
                "type": "consu",
                "is_storable": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.vendor_1.id,
                            "min_qty": 1.0,
                            "price": 10.0,
                            "delay": 5,  # lead time 5 days
                        }
                    )
                ],
            }
        )

        # create Bill of Materials
        self.bom_1 = self.Bom.create(
            {
                "product_id": self.product_to_manufacture.id,
                "product_tmpl_id": self.product_to_manufacture.product_tmpl_id.id,
                "product_uom_id": self.product_to_manufacture.uom_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.clear(),
                    Command.create(
                        {
                            "product_id": component_for_product.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )

    @freeze_time("2024-01-01 10:00:00")
    def test_01_(self):
        today = datetime.today()
        self.env.company.manufacturing_lead = 3  # security lead time of 3 days
        # create Orderpoint for product to manufacture
        self.orderpoint_ptm = self.Orderpoint.create(
            {
                "name": "OP_XYZ_1",
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_id": self.product_to_manufacture.id,
                "product_min_qty": 1.0,
                "product_max_qty": 1.0,
                "product_uom": self.product_to_manufacture.uom_id.id,
            }
        )
        current_production_ids = self.Production.search([])
        self.ProcurementGroup.run_scheduler()
        # ensure that a production order has been created by orderpoint
        new_production_ids = self.Production.search([]) - current_production_ids
        # check that the production order start date takes into account
        # the supplier delay of the component in BoM
        self.assertEqual(len(new_production_ids), 1)
        expected_date_start = today + timedelta(days=5)
        self.assertEqual(
            new_production_ids.date_start,
            expected_date_start,
        )
        # compute expected finished date
        max_delay = max(self.bom_1.bom_line_ids.mapped("delay")) + 3
        expected_date_finished = today + timedelta(days=max_delay)
        # self.assertEqual(
        #     new_production_ids.date_finished,
        #     expected_date_finished,
        # )
