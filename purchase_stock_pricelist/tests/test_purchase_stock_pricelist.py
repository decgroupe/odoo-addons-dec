# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.addons.purchase_pricelist.tests.common import TestPurchasePricelistCommon


class TestPurchaseStockPricelist(TestPurchasePricelistCommon):
    """ """

    def setUp(self):
        super().setUp()
        self.stock_location = self.env["ir.model.data"].xmlid_to_object(
            "stock.stock_location_stock"
        )
        self.customer_location = self.env["ir.model.data"].xmlid_to_object(
            "stock.stock_location_customers"
        )

    def _create_move(self, name, product_id, loc_src, loc_dst):
        move_id = self.env["stock.move"].create(
            {
                "name": name,
                "location_id": loc_src.id,
                "location_dest_id": loc_dst.id,
                "product_id": product_id.id,
                "product_uom": product_id.uom_id.id,
                "product_uom_qty": 1.0,
                "procure_method": "make_to_order",
            }
        )
        return move_id

    def test_01_mto(self):
        pricelist_id = self._create_pricelist_with_default_item(
            "Purchase PriceList (default)", "standard_price"
        )
        supplier_id = self._create_supplier("MySupplier", pricelist_id)
        vals = self._get_default_product_values(supplier_id)
        product_id = self._create_product("MyProduct", vals)
        # create and confirm a first move
        customer_move1 = self._create_move(
            "Move #1", product_id, self.stock_location, self.customer_location
        )
        customer_move1._action_confirm()
        purchase_order = self.env["purchase.order"].search(
            [("partner_id", "=", supplier_id.id)]
        )
        self.assertTrue(purchase_order)
        purchase_order_line = purchase_order.order_line
        # check that the price match the pricelist rule
        self.assertEqual(purchase_order_line.price_unit, 800)
        self.assertEqual(purchase_order_line.product_uom_qty, 1)
        self.assertEqual(purchase_order_line.price_subtotal, 800)
        # create and confirm a second move
        customer_move2 = self._create_move(
            "Move #2", product_id, self.stock_location, self.customer_location
        )
        customer_move2._action_confirm()
        # check that the price match the pricelist rule
        self.assertEqual(purchase_order_line.price_unit, 800)
        self.assertEqual(purchase_order_line.product_uom_qty, 2)
        self.assertEqual(purchase_order_line.price_subtotal, 1600)
