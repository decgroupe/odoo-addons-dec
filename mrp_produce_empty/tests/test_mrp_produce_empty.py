# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProduceEmpty(TransactionCase):

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def _create_product(self, name, type, route_ids=[]):
        return self.env["product.product"].create(
            {"name": name, "type": type, "route_ids": route_ids}
        )

    def setUp(self):
        super().setUp()
        self.prod1 = self._create_product("Product #1", "product")
        self.prod2 = self._create_product("Product #2", "product")
        self.consu1 = self._create_product("Consumable #1", "consu")
        # create Bill of Materials for Product #2
        self.prod2bom = self.env["mrp.bom"].create(
            {
                "product_id": self.prod2.id,
                "product_tmpl_id": self.prod2.product_tmpl_id.id,
                "product_uom_id": self.prod2.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.consu1.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )

    def test_01_confirm_mo_without_moves(self):
        production_id = self._generate_mo(self.prod1, bom=self.env["mrp.bom"], qty=5.0)
        self.assertFalse(production_id.move_raw_ids)
        production_id.action_confirm()
        self.assertEqual(production_id.state, "done")
        self.assertEqual(production_id.reservation_state, "assigned")
        self.assertEqual(production_id.qty_producing, 5.0)
        self.assertEqual(production_id.move_finished_ids.state, "done")

    def test_02_confirm_both_mo(self):
        p1_id = self._generate_mo(self.prod1, bom=self.env["mrp.bom"], qty=5.0)
        p2_id = self._generate_mo(self.prod2, bom=self.prod2bom, qty=2.0)
        production_ids = p1_id | p2_id
        production_ids.action_confirm()
        self.assertEqual(p1_id.state, "done")
        self.assertEqual(p2_id.state, "confirmed")
