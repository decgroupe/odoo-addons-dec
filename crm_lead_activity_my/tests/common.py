# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestCrmLeadActivityMyCommon(TransactionCase):
    """Base class for crm_lead_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.stage = cls.env["crm.stage"].search([], limit=1)
        cls.lead = cls.env["crm.lead"].create(
            {
                "name": "Test Lead",
                "type": "opportunity",
                "stage_id": cls.stage.id,
            }
        )
        cls.activity_type = cls.env.ref("mail.mail_activity_data_todo")
