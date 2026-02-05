# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestL10nFrBaseLocationDepartment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResCityZip = self.env["res.city.zip"]
        self.ResCity = self.env["res.city"]

    def test_01_field_names(self):
        self.assertIn("department_id", self.ResCityZip._fields)
