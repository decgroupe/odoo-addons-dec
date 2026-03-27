# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpChangeBom(TransactionCase):
    """Tests for mrp_change_bom module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.product_tmpl = cls.env["product.template"].create(
            {"name": "Finished Product"}
        )
        cls.product = cls.product_tmpl.product_variant_id
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_tmpl.id,
                "product_id": cls.product.id,
                "type": "normal",
            }
        )
        cls.bom2 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_tmpl.id,
                "product_id": cls.product.id,
                "type": "normal",
            }
        )
        cls.production = cls.env["mrp.production"].create(
            {
                "product_id": cls.product.id,
                "bom_id": cls.bom.id,
                "product_qty": 1,
            }
        )

    def test_01_bom_editable_in_form_when_draft_and_unlocked(self):
        """bom_id can be changed in form view when MO is in draft and unlocked."""
        self.assertEqual(self.production.state, "draft")
        self.production.is_locked = False
        with Form(self.production) as form:
            form.bom_id = self.bom2
        self.assertEqual(self.production.bom_id, self.bom2)

    def test_02_bom_editable_in_form_when_confirmed_and_unlocked(self):
        """bom_id can be changed in form view when MO is confirmed but not locked."""
        self.production.action_confirm()
        self.production.is_locked = False
        with Form(self.production) as form:
            form.bom_id = self.bom
        self.assertEqual(self.production.bom_id, self.bom)

    def test_03_bom_readonly_in_form_when_confirmed_and_locked(self):
        """bom_id is readonly in form view when MO is confirmed and locked."""
        self.production.action_confirm()
        self.production.is_locked = True
        self.assertNotEqual(self.production.state, "draft")
        self.assertTrue(self.production.is_locked)
        with Form(self.production) as form:
            with self.assertRaises(AssertionError):
                form.bom_id = self.bom2
