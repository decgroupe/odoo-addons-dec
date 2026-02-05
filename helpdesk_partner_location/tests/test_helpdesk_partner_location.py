# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestHelpdeskPartnerLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.HelpdeskTicket = self.env["helpdesk.ticket"]

    def test_01_field_names(self):
        self.assertIn("partner_zip_id", self.HelpdeskTicket._fields)
        self.assertIn("partner_city_id", self.HelpdeskTicket._fields)
