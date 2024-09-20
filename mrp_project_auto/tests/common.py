# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests import Form
from odoo.tests import new_test_user
from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpProjectAutoCommon(TestMrpCommon):

    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.production_user = new_test_user(
            self.env,
            login="mrp_project_auto-production_user",
            groups="mrp.group_mrp_user",
            context=ctx,
        )
        self.product1 = self.env.ref("product.product_product_6")
        product_to_use_1 = self.env["product.product"].create(
            {
                "name": "Pr1",
                "type": "product",
            }
        )
        product_to_use_2 = self.env["product.product"].create(
            {
                "name": "Pr2",
                "type": "product",
            }
        )
        self.product1_bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product1.id,
                "product_tmpl_id": self.product1.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": product_to_use_1.id, "product_qty": 1},
                    ),
                    (
                        0,
                        0,
                        {"product_id": product_to_use_2.id, "product_qty": 1},
                    ),
                ],
            }
        )

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo
