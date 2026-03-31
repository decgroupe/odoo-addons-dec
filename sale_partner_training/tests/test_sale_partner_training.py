# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSalePartnerTraining(TransactionCase):
    """Tests for sale_partner_training module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.training = cls.env["res.partner.training"].create({"name": "Test Training"})
        cls.specialty_1 = cls.env["res.partner.training.specialty"].create(
            {"name": "Specialty A", "training_id": cls.training.id}
        )
        cls.specialty_2 = cls.env["res.partner.training.specialty"].create(
            {"name": "Specialty B", "training_id": cls.training.id}
        )
        cls.pricelist = cls.env["product.pricelist"].search([], limit=1)

    def _make_order(self, specialties=None):
        """Create a sale order with optional training specialties."""
        vals = {
            "partner_id": self.partner.id,
        }
        if specialties:
            vals["training_specialty_ids"] = [Command.link(s.id) for s in specialties]
        return self.env["sale.order"].create(vals)

    def test_01_field_exists(self):
        """sale.order has the training_specialty_ids field."""
        order = self._make_order()
        self.assertFalse(order.training_specialty_ids)

    def test_02_link_specialty(self):
        """Training specialties can be linked to a sale order."""
        order = self._make_order(specialties=self.specialty_1)
        self.assertEqual(order.training_specialty_ids, self.specialty_1)

    def test_03_link_multiple_specialties(self):
        """Multiple training specialties can be linked to a sale order."""
        order = self._make_order(specialties=self.specialty_1 | self.specialty_2)
        self.assertEqual(len(order.training_specialty_ids), 2)
        self.assertIn(self.specialty_1, order.training_specialty_ids)
        self.assertIn(self.specialty_2, order.training_specialty_ids)

    def test_04_update_specialties(self):
        """Training specialties on a sale order can be updated."""
        order = self._make_order(specialties=self.specialty_1)
        self.assertEqual(order.training_specialty_ids, self.specialty_1)
        order.write({"training_specialty_ids": [Command.link(self.specialty_2.id)]})
        self.assertIn(self.specialty_1, order.training_specialty_ids)
        self.assertIn(self.specialty_2, order.training_specialty_ids)

    def test_05_clear_specialties(self):
        """Training specialties on a sale order can be cleared."""
        order = self._make_order(specialties=self.specialty_1 | self.specialty_2)
        self.assertEqual(len(order.training_specialty_ids), 2)
        order.write({"training_specialty_ids": [Command.clear()]})
        self.assertFalse(order.training_specialty_ids)
