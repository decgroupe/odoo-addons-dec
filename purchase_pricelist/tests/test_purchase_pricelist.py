# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

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
        self.assertEqual(product_id.seller_ids[0].price, 0)
        self.assertEqual(purchase_order_id.order_line[0].price_unit, 1000)
