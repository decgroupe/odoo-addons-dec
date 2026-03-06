# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestMrpPartnerAcademy(TransactionCase):
    """Test the mrp_partner_academy module."""

    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]

    def test_01_field_names(self):
        self.assertIn("partner_academy_id", self.production_model._fields)
