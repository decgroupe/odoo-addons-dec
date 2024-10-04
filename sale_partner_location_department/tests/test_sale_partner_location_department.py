# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestSalePartnerLocationDepartment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.sale_order_model = self.env["sale.order"]

    def test_01_field_names(self):
        self.assertIn("partner_shipping_department_id", self.sale_order_model._fields)
        self.assertIn("partner_shipping_state_id", self.sale_order_model._fields)
