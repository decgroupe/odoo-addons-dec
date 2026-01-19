# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestProductSeller(TransactionCase):
    """Test Product Template Main Seller"""

    def _create_product_tmpl(self, name):
        return self.env["product.template"].create(
            {
                "name": name,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

    def _create_supplierinfo(
        self, partner_id, product_tmpl_id, min_qty, price, sequence=1
    ):
        return self.env["product.supplierinfo"].create(
            {
                "partner_id": partner_id,
                "product_tmpl_id": product_tmpl_id,
                "min_qty": min_qty,
                "price": price,
                "sequence": sequence,
            }
        )

    def setUp(self):
        super().setUp()
        self.partner_a = self.env.ref("base.res_partner_2")
        self.partner_b = self.env.ref("base.res_partner_3")
        self.prod_tmpl1 = self._create_product_tmpl("Product Tmpl 1")
        self.supplierinfo_a = self._create_supplierinfo(
            partner_id=self.partner_a.id,
            product_tmpl_id=self.prod_tmpl1.id,
            min_qty=1,
            price=10.0,
        )
        self.supplierinfo_b = self._create_supplierinfo(
            partner_id=self.partner_b.id,
            product_tmpl_id=self.prod_tmpl1.id,
            min_qty=1,
            price=12.0,
        )
        # set supplierinfo details
        self.supplierinfo_a.product_code = "PA-001"
        self.supplierinfo_a.product_name = "Product A"
        self.supplierinfo_a.delay = 5
        self.supplierinfo_b.product_code = "PB-001"
        self.supplierinfo_b.product_name = "Product B"
        self.supplierinfo_b.delay = 3

    def test_01_product_template_main_supplier(self):
        # check main seller
        self.assertEqual(self.prod_tmpl1.main_seller_id.partner_id, self.partner_a)
        # set a lower price for supplierinfo_b
        self.supplierinfo_b.price = 8.0
        # check main seller is now supplierinfo_b
        self.assertEqual(self.prod_tmpl1.main_seller_id.partner_id, self.partner_b)
        # set a minimum quantity for supplierinfo_b
        self.supplierinfo_b.min_qty = 5
        # check main seller is still supplierinfo_b (since min_qty is ignored used
        # in main seller computation)
        self.assertEqual(self.prod_tmpl1.main_seller_id.partner_id, self.partner_b)
        # deactivate partner_b
        self.partner_b.active = False
        # check main seller is now supplierinfo_a
        self.assertEqual(self.prod_tmpl1.main_seller_id.partner_id, self.partner_a)
        # deactivate partner_a
        self.partner_a.active = False
        # check no main seller
        self.assertFalse(self.prod_tmpl1.main_seller_id)

    def test_02_product_template_main_supplier_related(self):
        # check related fields values
        self.assertEqual(self.prod_tmpl1.seller_id, self.partner_a)
        self.assertEqual(
            self.prod_tmpl1.seller_product_code, self.supplierinfo_a.product_code
        )
        self.assertEqual(
            self.prod_tmpl1.seller_product_name, self.supplierinfo_a.product_name
        )
        # set a lower price for supplierinfo_b
        self.supplierinfo_b.price = 8.0
        # check related fields values are updated
        self.assertEqual(self.prod_tmpl1.seller_id, self.partner_b)
        self.assertEqual(
            self.prod_tmpl1.seller_product_code, self.supplierinfo_b.product_code
        )
        self.assertEqual(
            self.prod_tmpl1.seller_product_name, self.supplierinfo_b.product_name
        )
        self.assertEqual(self.prod_tmpl1.seller_delay, self.supplierinfo_b.delay)
        self.assertEqual(self.prod_tmpl1.seller_delay, 3)
        # change delay for supplierinfo_b
        self.supplierinfo_b.delay = 10
        # check related field value is updated
        self.assertEqual(self.prod_tmpl1.seller_delay, 10)
