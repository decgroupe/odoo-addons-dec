# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2023

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpBomOrder(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.myproduct = self.env["product.product"].create({"name": "MyProduct"})
        self.mybom_v1 = self._create_bom(self.myproduct, "MPV1", 1)

    def _create_bom(self, product, code, sequence):
        bom = self.env["mrp.bom"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "code": code,
                "sequence": sequence,
            }
        )
        return bom

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def test_01_no_new_bom(self):
        production_id = self._generate_mo(self.myproduct, self.mybom_v1)
        self.assertFalse(production_id.newer_bom_id)

    def test_02_new_bom_lower_sequence(self):
        bom_v2 = self._create_bom(self.myproduct, "MPV2", 0)
        production_id = self._generate_mo(self.myproduct, self.mybom_v1)
        self.assertFalse(production_id.newer_bom_id)

    def test_03_newer_bom(self):
        bom_v2 = self._create_bom(self.myproduct, "MPV2", 2)
        production_id = self._generate_mo(self.myproduct, self.mybom_v1)
        self.assertEqual(production_id.newer_bom_id, bom_v2)

    def test_04_newer_bom_with_alt_code(self):
        bom_v0 = self._create_bom(self.myproduct, "MPV0", 2)
        production_id = self._generate_mo(self.myproduct, self.mybom_v1)
        self.assertEqual(production_id.newer_bom_id, bom_v0)
