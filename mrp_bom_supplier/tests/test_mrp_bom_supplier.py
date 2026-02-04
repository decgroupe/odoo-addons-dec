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
        sub_product_a = self.Product.create(
            {
                "name": "Sub Product A",
                "type": "consu",
            }
        )
        sub_product_b = self.Product.create(
            {
                "name": "Sub Product B",
                "type": "consu",
            }
        )

        self.product_to_manufacture = self.Product.create(
            {
                "name": "Test Product",
                "route_ids": [Command.set(route_manuf.ids)],
                "type": "consu",
                "is_storable": True,
            }
        )
        self.component_to_buy_for_product = self.Product.create(
            {
                "name": "Test component to buy",
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
        self.component_to_manufacture_for_product = self.Product.create(
            {
                "name": "Test component to manufacture",
                "route_ids": [Command.set(route_manuf.ids + route_mto.ids)],
                "type": "consu",
                "is_storable": True,
                "bom_ids": [
                    Command.clear(),
                    Command.create(
                        {
                            "product_qty": 1.0,
                            "produce_delay": 4,
                            "bom_line_ids": [
                                Command.clear(),
                                Command.create(
                                    {
                                        "product_id": sub_product_a.id,
                                        "product_qty": 1.0,
                                    }
                                ),
                                Command.create(
                                    {
                                        "product_id": sub_product_b.id,
                                        "product_qty": 1.0,
                                    }
                                ),
                            ],
                        }
                    ),
                ],
            }
        )

        # create Bill of Materials
        self.bom_for_product = self.Bom.create(
            {
                "product_tmpl_id": self.product_to_manufacture.product_tmpl_id.id,
                # "product_id": self.product_to_manufacture.id,
                "product_uom_id": self.product_to_manufacture.uom_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.clear(),
                    Command.create(
                        {
                            "product_id": self.component_to_buy_for_product.id,
                            "product_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.component_to_manufacture_for_product.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )

    @freeze_time("2024-01-01 10:00:00")
    def test_01_dates(self):
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
        # ensure that two production orders have been created:
        # - one by orderpoint for the finished product
        # - one by the BoM line for the component to manufacture
        new_production_ids = self.Production.search([]) - current_production_ids
        self.assertEqual(len(new_production_ids), 2)

    def test_02_bom_line_seller_and_delay(self):
        # get values from bom lines
        bom_line_1 = self.bom_for_product.bom_line_ids[0]
        self.assertEqual(bom_line_1.seller_id.partner_id, self.vendor_1)
        self.assertEqual(bom_line_1.delay, 5)  # vendor delay
        bom_line_2 = self.bom_for_product.bom_line_ids[1]
        self.assertFalse(bom_line_2.seller_id)
        self.assertEqual(bom_line_2.delay, 4)  # produce delay
        # modify delays and check that values are propagated
        bom_line_1.delay = 7
        self.assertEqual(bom_line_1.seller_id.delay, 7)
        bom_line_2.delay = 10
        bom_component = self.env["mrp.bom"]._bom_find(bom_line_2.product_id)[
            bom_line_2.product_id
        ]
        self.assertEqual(bom_component.produce_delay, 10)

    def test_03_bom_line_partner(self):
        # create a new vendor
        vendor_2 = self.env["res.partner"].create(
            {"name": "Vendor 2", "supplier_rank": 1}
        )
        # bom_line_1 = self.bom_for_product.bom_line_ids[0]
        # bom_line_1.partner_id = vendor_2
        # create a new supplierinfo for vendor 2
        self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor_2.id,
                "product_tmpl_id": self.component_to_buy_for_product.product_tmpl_id.id,
                "min_qty": 1.0,
                "price": 12.0,
                "delay": 8,
            }
        )
        # assign vendor 2 to bom line
        bom_line_1 = self.bom_for_product.bom_line_ids[0]
        bom_line_1.partner_id = vendor_2
        # check that bom line seller and delay are updated
        self.assertEqual(bom_line_1.seller_id.partner_id, vendor_2)
        self.assertEqual(bom_line_1.delay, 8)
