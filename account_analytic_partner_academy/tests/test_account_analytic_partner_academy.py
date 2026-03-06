# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023


from odoo.tests import common


class TestAccountAnalyticPartnerAcademy(common.TransactionCase):
    """Test the account_analytic_partner_academy module."""

    def setUp(self):
        super().setUp()
        self.account_analytic_line_model = self.env["account.analytic.line"]

    def test_01_field_names(self):
        self.assertIn("partner_academy_id", self.account_analytic_line_model._fields)
