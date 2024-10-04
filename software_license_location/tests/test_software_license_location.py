# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestSoftwareLicenseLocation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.license_model = self.env["software.license"]

    def test_01_field_names(self):
        self.assertIn("partner_zip_id", self.license_model._fields)
        self.assertIn("partner_city_id", self.license_model._fields)
