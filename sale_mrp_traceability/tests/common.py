# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleMrpTraceabilityCommon(TransactionCase):
    """Common setup for sale_mrp_traceability tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.group_mrp_traceability = cls.env.ref(
            "sale_mrp_traceability.group_sale_mrp_traceability"
        )
        cls.env.user.write({"groups_id": [Command.link(cls.group_mrp_traceability.id)]})
