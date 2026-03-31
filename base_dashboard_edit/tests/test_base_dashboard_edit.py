# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestBaseDashboardEdit(TransactionCase):
    """Tests for base_dashboard_edit module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.ViewCustom = cls.env["ir.ui.view.custom"]
        cls.base_view = cls.env.ref("base.view_view_custom_form")
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.demo_user = cls.env.ref("base.user_demo")

    def _create_custom_view(self, user, arch="<form/>"):
        """Create an ir.ui.view.custom record for the given user."""
        return self.ViewCustom.sudo().create(
            {
                "user_id": user.id,
                "ref_id": self.base_view.id,
                "arch": arch,
            }
        )

    def test_01_create_date_field_exists(self):
        """create_date field must exist on ir.ui.view.custom."""
        custom = self._create_custom_view(self.demo_user)
        self.assertTrue(custom.create_date, "create_date must be set after creation")

    def test_02_create_date_field_indexed(self):
        """create_date must be declared with index=True on ir.ui.view.custom."""
        field = self.ViewCustom._fields.get("create_date")
        self.assertIsNotNone(field, "create_date field must exist")
        self.assertTrue(
            getattr(field, "index", False),
            "create_date must be indexed",
        )

    def test_03_admin_can_see_all_custom_views(self):
        """Admin user must be able to read all ir.ui.view.custom records."""
        custom_demo = self._create_custom_view(self.demo_user)
        # admin reads without sudo — the custom security rule allows it
        result = self.ViewCustom.with_user(self.admin_user).search(
            [("id", "=", custom_demo.id)]
        )
        self.assertTrue(
            result,
            "admin must be able to read custom views belonging to other users",
        )

    def test_04_regular_user_has_no_direct_acl_access(self):
        """A regular (non-admin) user must not have direct ACL access to
        `ir.ui.view.custom`."""
        self._create_custom_view(self.admin_user)
        with self.assertRaises(AccessError):
            self.ViewCustom.with_user(self.demo_user).search([])
