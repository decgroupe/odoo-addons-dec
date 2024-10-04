# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestMrpPartnerLocationDepartment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]

    def test_01_field_names(self):
        self.assertIn("partner_department_id", self.production_model._fields)
        self.assertIn("partner_state_id", self.production_model._fields)
