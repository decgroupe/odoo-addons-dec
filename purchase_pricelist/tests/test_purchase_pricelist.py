# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo import Command

from odoo.addons.purchase_pricelist.tests.common import TestPurchasePricelistCommon


class TestPurchasePricelist(TestPurchasePricelistCommon):
    """ """

    def setUp(self):
        super().setUp()

    def test_01_standard_price_from_pricelist(self):
        pricelist_id = self._create_pricelist_with_default_item(
            "Purchase PriceList (default)", "standard_price"
        )
        supplier_id = self._create_supplier("MySupplier", pricelist_id)
        vals = self._get_default_product_values(supplier_id)
        product_id = self._create_product("MyProduct", vals)
        purchase_order_id = self._create_purchase_order(supplier_id, product_id)
        self.assertEqual(purchase_order_id.pricelist_id, pricelist_id)
        self.assertEqual(product_id.seller_ids[0].price, 0)
        self.assertEqual(purchase_order_id.order_line[0].price_unit, 800)

    def test_02_list_price_from_pricelist(self):
        pricelist_id = self._create_pricelist_with_default_item(
            "Purchase PriceList (default)", "list_price"
        )
        supplier_id = self._create_supplier("MySupplier", pricelist_id)
        vals = self._get_default_product_values(supplier_id)
        product_id = self._create_product("MyProduct", vals)
        purchase_order_id = self._create_purchase_order(supplier_id, product_id)
        self.assertEqual(purchase_order_id.pricelist_id, pricelist_id)
        self.assertEqual(product_id.seller_ids[0].price, 0)
        self.assertEqual(purchase_order_id.order_line[0].price_unit, 1000)

    def test_03(self):
        # pricelist based on supplierinfo price
        pricelist_id = self._create_pricelist_with_default_item(
            "Purchase PriceList (default)", "supplierinfo"
        )
        # edit the default item to have a surchage of 10
        pricelist_item_id = self.pricelist_item_model.search(
            [("pricelist_id", "=", pricelist_id.id)]
        )
        pricelist_item_id.write({"price_surcharge": 10})
        # create multiple suppliers for different prices but with the same pricelist
        supplier1 = self._create_supplier("Supplier#1", pricelist_id)
        supplier2 = self._create_supplier("Supplier#2", pricelist_id)
        supplier3 = self._create_supplier("Supplier#3", pricelist_id)
        vals = self._get_default_product_values(supplier1, seller_price=810)
        vals["seller_ids"].extend(
            [
                Command.create(
                    {
                        "sequence": 2,
                        "partner_id": supplier2.id,
                        "min_qty": 1.0,
                        "price": 850,
                    }
                ),
                Command.create(
                    {
                        "sequence": 3,
                        "partner_id": supplier3.id,
                        "min_qty": 1.0,
                        "price": 830,
                    }
                ),
            ]
        )
        product_id = self._create_product("MyProduct", vals)
        self.assertEqual(product_id.seller_ids[0].partner_id, supplier1)
        self.assertEqual(product_id.seller_ids[1].partner_id, supplier2)
        self.assertEqual(product_id.seller_ids[2].partner_id, supplier3)
        # product_id.env.cr.commit()
        # print(1)
        # check prices from each seller
        for seller, expected_price in [
            (product_id.seller_ids[0], 820),  # 810 + 10
            (product_id.seller_ids[1], 860),  # 850 + 10
            (product_id.seller_ids[2], 840),  # 830 + 10
        ]:
            self.assertEqual(seller.list_price, expected_price)
            supplier = seller.partner_id
            purchase_order_id = self._create_purchase_order(supplier, product_id)
            self.assertEqual(purchase_order_id.pricelist_id, pricelist_id)
            self.assertEqual(purchase_order_id.order_line[0].price_unit, expected_price)
