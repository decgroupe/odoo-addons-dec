# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestMrpBomProductState(TransactionCase):
    """Tests for mrp_bom_product_state module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.state = cls.env["product.state"].create(
            {"name": "Test State", "code": "test"}
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {"name": "Test Product", "type": "consu"}
        )
        cls.bom = cls.env["mrp.bom"].create({"product_tmpl_id": cls.product_tmpl.id})

    def test_01_state_from_template_visible_on_bom(self):
        """Test that the product state set on the template is visible on the bom."""
        self.product_tmpl.product_state_id = self.state
        self.assertEqual(self.bom.product_state_id, self.state)

    def test_02_state_writable_via_bom(self):
        """Test that writing product_state_id on the bom propagates to the template."""
        self.bom.product_state_id = self.state
        self.assertEqual(self.product_tmpl.product_state_id, self.state)
