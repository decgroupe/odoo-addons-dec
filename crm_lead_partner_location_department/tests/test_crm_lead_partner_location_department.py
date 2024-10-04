# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestCrmLeadPartnerLocationDepartment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.lead_model = self.env["crm.lead"]

    def test_01_field_names(self):
        self.assertIn("partner_department_id", self.lead_model._fields)
        self.assertIn("partner_state_id", self.lead_model._fields)
        self.assertIn("partner_shipping_department_id", self.lead_model._fields)
        self.assertIn("partner_shipping_state_id", self.lead_model._fields)
