# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestProcurementTraceabilitySaleCommon(TransactionCase):
    """Common setup for procurement_traceability_sale tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.ProcurementGroup = cls.env["procurement.group"]
        cls.SaleOrder = cls.env["sale.order"]
        # create a partner for sale orders
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        # create a procurement group
        cls.group = cls.ProcurementGroup.create({"name": "TEST/001"})
        # create a sale order linked to the group
        cls.sale_order = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "procurement_group_id": cls.group.id,
            }
        )
