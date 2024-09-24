# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpPurchaseCommon(TransactionCase):

    def setUp(self):
        super(TestMrpPurchaseCommon, self).setUp()

        # Create products
        self.obj_warehouse = self.env["stock.warehouse"]
        self.test_wh = self.obj_warehouse.create(
            {
                "name": "Test WH",
                "code": "T",
            }
        )
        self.supplier = self.env["res.partner"].create(
            {
                "name": "Supplier",
            }
        )
        self.product_model = self.env["product.product"]
        self.p1 = self.product_model.create(
            {
                "name": "101",
                "type": "product",
            }
        )
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
        self.stock_product = self.product_model.create(
            {
                "name": "Stockable Product",
                "type": "product",
            }
        )
        self.service.property_subcontracted_service = True
        # Create bill of materials
        self.bom_model = self.env["mrp.bom"]
        self.bom = self.bom_model.create(
            {
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "product_id": self.p1.id,
                "product_qty": 1,
                "type": "normal",
            }
        )
        # Add at least one stock product or Odoo will complain about adding
        # raw materials
        self.bom_line_model = self.env["mrp.bom.line"]
        self.bom_line_model.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.stock_product.id,
                "product_qty": 1,
            }
        )

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo
