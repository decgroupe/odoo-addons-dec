# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestCrmLeadPartnerAcademy(TransactionCase):
    """Test the crm_lead_partner_academy module."""

    def setUp(self):
        super().setUp()
        self.crm_lead_model = self.env["crm.lead"]

    def test_01_field_names(self):
        self.assertIn("partner_academy_id", self.crm_lead_model._fields)
        self.assertIn("partner_shipping_academy_id", self.crm_lead_model._fields)
