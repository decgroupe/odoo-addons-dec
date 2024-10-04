# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestAccountPartnerLocationDepartment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.account_move_model = self.env["account.move"]
        self.account_move_line_model = self.env["account.move.line"]

    def test_01_field_names(self):
        self.assertIn("partner_department_id", self.account_move_model._fields)
        self.assertIn("partner_state_id", self.account_move_model._fields)
        self.assertIn("partner_department_id", self.account_move_line_model._fields)
        self.assertIn("partner_state_id", self.account_move_line_model._fields)
