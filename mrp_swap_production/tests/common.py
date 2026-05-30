# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class FakeSwapObject(dict):
    """Dictionary-backed object supporting both item and attribute access."""

    def __init__(self, values=None, **attributes):
        """Initialize the fake record with mapping values and attributes."""
        super().__init__(values or {})
        for name, value in attributes.items():
            setattr(self, name, value)


class TestMrpSwapProductionCommon(TransactionCase):
    """Shared fixtures for mrp_swap_production tests."""

    @classmethod
    def setUpClass(cls):
        """Create reusable products, requests and manufacturing fixtures."""
        super().setUpClass()
        cls.WizardModel = cls.env["mrp.swap.production"]
        cls.WizardLineModel = cls.env["mrp.swap.production.line"]
        cls.ProductionModel = cls.env["mrp.production"]
        cls.RequestModel = cls.env["mrp.production.request"]
        cls.product = cls.env.ref("product.product_product_3")
        cls.product.write({"mrp_production_request": True})
        cls.bom = cls.product.bom_ids[:1]
        cls.partner = cls.env.ref("base.res_partner_1")

    def _create_production(self, qty=1.0):
        """Create and confirm a production order for the shared product."""
        production = self.ProductionModel.create(
            {
                "product_id": self.product.id,
                "product_qty": qty,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        return production

    def _create_request(self, qty=1.0, partner=None):
        """Create a production request matching the shared demo product."""
        values = {
            "product_id": self.product.id,
            "product_qty": qty,
            "bom_id": self.bom.id,
        }
        if partner:
            values["partner_id"] = partner.id
        return self.RequestModel.create(values)

    def _create_wizard(self, production_a=None, production_b=None):
        """Create the swap wizard for two productions."""
        production_a = production_a or self._create_production()
        production_b = production_b or self._create_production()
        return self.WizardModel.create(
            {
                "this_production_id": production_a.id,
                "other_production_id": production_b.id,
            }
        )

    def _attach_lines(self, wizard, productions):
        """Attach swap lines to a wizard for the provided production pairs."""
        line_ids = self.WizardLineModel.browse()
        for source, destination, swap_final_moves in productions:
            line_ids += self.WizardLineModel.create(
                {
                    "product_id": self.product.id,
                    "from_production_id": source.id,
                    "to_production_id": destination.id,
                    "swap_final_moves": swap_final_moves,
                }
            )
        wizard.write({"swap_line_ids": [Command.set(line_ids.ids)]})
        return line_ids
