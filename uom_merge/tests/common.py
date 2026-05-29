# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestUomMergeCommon(TransactionCase):
    """Base class for uom_merge tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.uom_model = cls.env["uom.uom"]
        cls.merge_uom_wizard_model = cls.env["merge.uom.uom.wizard"]
        cls.group_do_merge = cls.env.ref("uom_merge.res_group_do_merge")
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user = new_test_user(
            cls.env,
            login="uom_merge-user",
            groups="base.group_user",
            context=ctx,
        )

    def _create_uom(self, name, category_id, uom_type="smaller", factor=1000.0):
        """Create a unit of measure for testing."""
        return self.uom_model.create(
            {
                "name": name,
                "category_id": category_id,
                "uom_type": uom_type,
                "factor": factor,
            }
        )
