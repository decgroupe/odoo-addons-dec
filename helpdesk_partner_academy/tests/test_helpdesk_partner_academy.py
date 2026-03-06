# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestHelpdeskPartnerAcademy(TransactionCase):
    """Test the helpdesk_partner_academy module."""

    def setUp(self):
        super().setUp()
        self.ticket_model = self.env["helpdesk.ticket"]

    def test_01_field_names(self):
        self.assertIn("partner_academy_id", self.ticket_model._fields)
