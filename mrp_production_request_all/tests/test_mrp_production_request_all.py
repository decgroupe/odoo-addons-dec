# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestMrpProductionRequestAll(TransactionCase):
    """Tests for mrp_production_request_all module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data: product, bom, and approved request of qty 3."""
        super().setUpClass()
        # create a storable product and a matching bom
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        # create a production request and manually approve it
        cls.request = cls.env["mrp.production.request"].create(
            {
                "product_id": cls.product.id,
                "product_qty": 3.0,
                "bom_id": cls.bom.id,
            }
        )
        cls.request.button_to_approve()
        cls.request.button_approved()

    def test_01_create_all_mo_creates_correct_count(self):
        """Calling create_all_manufacturing_orders creates one MO per pending unit."""
        self.assertEqual(self.request.pending_qty, 3.0)
        self.request.create_all_manufacturing_orders()
        mos = self.env["mrp.production"].search(
            [("mrp_production_request_id", "=", self.request.id)]
        )
        self.assertEqual(len(mos), 3)

    def test_02_each_mo_has_qty_one(self):
        """Each manufacturing order created has a quantity of exactly 1."""
        mos = self.env["mrp.production"].search(
            [("mrp_production_request_id", "=", self.request.id)]
        )
        for mo in mos:
            self.assertEqual(mo.product_qty, 1.0)
