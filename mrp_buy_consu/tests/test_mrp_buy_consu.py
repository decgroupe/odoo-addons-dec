# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class TestMrpBuyConsu(TransactionCase):
    """ """

    def _create_product(self, name, type, route_ids=[]):
        return self.env["product.product"].create(
            {"name": name, "type": type, "route_ids": route_ids}
        )

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.bom_line_model = self.env["mrp.bom.line"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_loc = self.env.ref("stock.stock_location_stock")
        route_manuf = self.env.ref("mrp.route_warehouse0_manufacture")
        # route_buy = self.warehouse.buy_pull_id.route_id
        route_mto = self.warehouse.mto_pull_id.route_id
        route_mto.active = True

        # create a fake route since buy route is not available here
        route_fakebuy = self.env["stock.location.route"].create(
            {
                "name": "Buy (Fake)",
                "product_selectable": True,
            }
        )
        route_fakebuy_rule0 = self.env["stock.rule"].create(
            {
                "route_id": route_fakebuy.id,
                "name": "Buy Rule (simple tranfert)",
                "action": "pull",
                # San Francisco: Receipts
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                # Partner Locations/Vendors
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                # WH/Stock
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.warehouse.company_id.id,
            }
        )

        # create products
        self.myproduct = self._create_product(
            "MyProduct", "product", route_ids=[(6, 0, [route_manuf.id, route_mto.id])]
        )
        # consumable product
        self.product_a = self._create_product(
            "Product A (consumable)", "consu", route_ids=[(6, 0, [route_fakebuy.id])]
        )
        # stockable product but available quantity should not be decreased in a
        # manufacturing process, only when manually moved from stock -> production
        self.product_b = self._create_product(
            "Product B (stockable)", "product", route_ids=[(6, 0, [route_fakebuy.id])]
        )
        self.product_b.small_supply = True

        # Create Bill of Materials:
        self.mybom = self.bom_model.create(
            {
                "product_id": self.myproduct.id,
                "product_tmpl_id": self.myproduct.product_tmpl_id.id,
                "product_uom_id": self.myproduct.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 1.0,
                            "buy_consumable": False,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b.id,
                            "product_qty": 1.0,
                            "buy_consumable": False,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_qty": 1.0,
                            "buy_consumable": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b.id,
                            "product_qty": 1.0,
                            "buy_consumable": True,
                        },
                    ),
                ],
            }
        )
        # self.env.cr.commit()

    def test_01_buy_consumable(self):
        production_id = self._generate_mo(self.myproduct, self.mybom)
        production_id.action_confirm()
        # extract created moves
        move_a = production_id.move_raw_ids[0]
        move_b = production_id.move_raw_ids[1]
        move_a_buy = production_id.move_raw_ids[2]
        move_b_buy = production_id.move_raw_ids[3]
        # ensure indexed move equals bom line creation order
        self.assertEqual(move_a.product_id, self.product_a)
        self.assertEqual(move_a.bom_line_id.buy_consumable, False)
        self.assertEqual(move_b.product_id, self.product_b)
        self.assertEqual(move_b.bom_line_id.buy_consumable, False)
        self.assertEqual(move_a_buy.product_id, self.product_a)
        self.assertEqual(move_a_buy.bom_line_id.buy_consumable, True)
        self.assertEqual(move_b_buy.product_id, self.product_b)
        self.assertEqual(move_b_buy.bom_line_id.buy_consumable, True)
        # ensure buyable and consumable moves have same locations
        self.assertEqual(move_a.location_id, move_a.location_dest_id)
        self.assertEqual(move_b.location_id, move_b.location_dest_id)
        # ensure procure method has been kept
        self.assertEqual(move_a.procure_method, "make_to_stock")
        self.assertEqual(move_b.procure_method, "make_to_stock")
        self.assertEqual(move_a_buy.procure_method, "make_to_order")
        self.assertEqual(move_b_buy.procure_method, "make_to_order")
        # ensure valid states
        self.assertEqual(move_a.state, "assigned")
        self.assertEqual(move_b.state, "assigned")
        self.assertEqual(move_a_buy.state, "waiting")
        self.assertEqual(move_b_buy.state, "waiting")
