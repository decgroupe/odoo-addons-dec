# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2023

from odoo.tests.common import TransactionCase


class TestMrpBomDates(TransactionCase):
    """Test the existence of the new fields on BoM"""

    def setUp(self):
        super().setUp()
        self.BoM = self.env["mrp.bom"]

    def test_01_field_names(self):
        self.assertIn("date_start", self.BoM._fields)
        self.assertIn("date_stop", self.BoM._fields)
