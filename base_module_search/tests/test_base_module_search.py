# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestBaseModuleSearch(TransactionCase):
    """Tests for base_module_search module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.IrModule = cls.env["ir.module.module"]

    def test_01_list_view_has_icon_image(self):
        """The list view of ir.module.module includes the icon_image field."""
        view = self.env.ref("base_module_search.ir_module_module_tree_view")
        self.assertTrue(view)
        self.assertIn("icon_image", view.arch)

    def test_02_kanban_learn_more_invisible(self):
        """The Learn More link in the kanban card is always invisible."""
        view = self.env.ref("base_module_search.module_kanban_view")
        self.assertTrue(view)
        # the xpath sets invisible=True on the Learn More anchor
        self.assertIn("invisible", view.arch)

    def test_03_action_view_mode_list_first(self):
        """The Apps action has list before kanban in view_mode."""
        action = self.env.ref("base.open_module_tree")
        self.assertTrue(action.view_mode.startswith("list"))
