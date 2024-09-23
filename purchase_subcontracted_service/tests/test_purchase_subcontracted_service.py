# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests.common import TransactionCase


class TestPurchaseSubcontractedService(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product_model = self.env["product.product"]
        self.supplier = self.env["res.partner"].create({"name": "Supplier"})
        self.service = self.product_model.create(
            {
                "name": "Galvanize Service",
                "type": "service",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.supplier.id,
                            "price": 100.0,
                        },
                    )
                ],
            }
        )

    def test_01_compute(self):
        self.assertFalse(self.service.property_subcontracted_service)
        self.service.property_subcontracted_service = True
        self.assertTrue(self.service.property_subcontracted_service)
        self.service.property_subcontracted_service = False
        self.assertFalse(self.service.property_subcontracted_service)

    def test_02_inverse1(self):
        self.assertFalse(self.service.property_subcontracted_service)
        self.service.service_to_purchase = True
        self.assertTrue(self.service.property_subcontracted_service)
        self.service.service_to_purchase = False
        self.assertFalse(self.service.property_subcontracted_service)

    def test_03_inverse2(self):
        self.assertFalse(self.service.service_to_purchase)
        self.service.product_tmpl_id.property_subcontracted_service = True
        self.assertTrue(self.service.product_tmpl_id.service_to_purchase)
        self.service.property_subcontracted_service = False
        self.assertFalse(self.service.service_to_purchase)

    # def test4(self):
    #     self.service.unidades = 4
    #     self.service.property_subcontracted_service = True
    #     print(self.service.unidades)
