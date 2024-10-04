# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023


from odoo.tests import common


class TestAccountAnalyticPartnerLocation(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.analytic_line_model = self.env["account.analytic.line"]

    def test_01_field_names(self):
        self.assertIn("partner_zip_id", self.analytic_line_model._fields)
        self.assertIn("partner_city_id", self.analytic_line_model._fields)
