# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestAccountActivityMyCommon(TransactionCase):
    """Common fixtures for account_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up model and inherited view used by the tests."""
        super().setUpClass()
        cls.AccountMove = cls.env["account.move"]
        cls.invoice_tree_view = cls.env.ref("account_activity_my.invoice_tree")
