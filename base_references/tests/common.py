# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026


from odoo import Command
from odoo.tests.common import TransactionCase


class TestBaseReferencesCommon(TransactionCase):
    """Base class with shared fixtures for base_references tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.IrModel = cls.env["ir.model"]
        cls.Partner = cls.env["res.partner"]
        cls.PartnerCategory = cls.env["res.partner.category"]
        cls.Wizard = cls.env["base.references.wizard"]
        cls.Result = cls.env["base.references.result"]
        # get ir.model records for commonly used models
        cls.partner_ir_model = cls.IrModel.search(
            [("model", "=", "res.partner")], limit=1
        )
        cls.category_ir_model = cls.IrModel.search(
            [("model", "=", "res.partner.category")], limit=1
        )
        # create a parent partner that will be referenced by a child
        cls.partner_parent = cls.Partner.create({"name": "Test Parent Partner"})
        cls.partner_child = cls.Partner.create(
            {
                "name": "Test Child Partner",
                "parent_id": cls.partner_parent.id,
            }
        )
        # create a category referenced by a partner via many2many
        cls.test_category = cls.PartnerCategory.create({"name": "Test Ref Category"})
        cls.partner_with_category = cls.Partner.create(
            {
                "name": "Test Categorized Partner",
                "category_id": [Command.link(cls.test_category.id)],
            }
        )

    def _create_wizard(self, model_id, res_id):
        """Create a base.references.wizard for the given model and record ID."""
        return self.Wizard.create(
            {
                "model_id": model_id,
                "res_id": res_id,
            }
        )
