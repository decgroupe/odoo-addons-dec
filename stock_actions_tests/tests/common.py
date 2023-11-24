# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.addons.stock_actions.tests.common import TestStockActionCommon
from odoo.exceptions import UserError
from odoo.tests import new_test_user


class TestStockActionTestsCommon(TestStockActionCommon):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.route_manufacture = cls.warehouse_1.manufacture_pull_id.route_id
        cls.route_buy = cls.warehouse_1.buy_pull_id.route_id

    def setUp(self):
        super(TestStockActionTestsCommon, self).setUp()
        self.assertTrue(self.route_mto.active)
        default_route_manufacture = self.env.ref("mrp.route_warehouse0_manufacture")
        default_route_buy = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.assertEqual(self.route_manufacture, default_route_manufacture)
        self.assertEqual(self.route_buy, default_route_buy)

    def _create_mto_customer_move(self):
        customer_move = self._send_to_customer(self.product, 5.0)
        customer_move.procure_method = "make_to_order"
        return customer_move