# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo.tests.common import TransactionCase


class TestProcurementLog(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProcurementGroup = self.env["procurement.group"]

    # def test_01_(self):
    #     product = self.env["product.product"].create({"name": "Test product"})
    #     self.ProcurementGroup._log_exception(product, "Test message", self.env.user)
    #     pass

    def test_02_(self):
        product_data = {"name": "Test product"}
        self.ProcurementGroup.test_create_product_exception(
            product_data, "Test message", self.env.user
        )
