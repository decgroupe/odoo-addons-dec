# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestPurchaseResponsibleAuto(TransactionCase):
    """Test the purchase responsible auto features"""

    def setUp(self):
        super().setUp()
        self.Order = self.env["purchase.order"]
        # create two new users
        self.user_a = new_test_user(
            self.env, login="purchaseusera", groups="purchase.group_purchase_user"
        )
        self.user_b = new_test_user(
            self.env, login="purchaseuserb", groups="purchase.group_purchase_user"
        )
        # references to existing purchase orders
        self.order_1 = self.env.ref("purchase.purchase_order_1")
        self.order_1.user_id = False
        self.order_2 = self.env.ref("purchase.purchase_order_2")
        self.order_2.user_id = self.env.ref("base.user_root")
        self.order_3 = self.env.ref("purchase.purchase_order_3")
        self.order_3.user_id = self.env.ref("base.user_admin")
        self.order_4 = self.env.ref("purchase.purchase_order_4")
        self.order_4.user_id = self.user_b

    def test_01_purchase_responsible_auto(self):
        """Test that the responsible is correctly set when printing a quotation"""
        # print quotation as user_a
        self.order_1.with_user(self.user_a).print_quotation()
        self.order_2.with_user(self.user_a).print_quotation()
        self.order_3.with_user(self.user_a).print_quotation()
        self.order_4.with_user(self.user_a).print_quotation()
        # check that the responsible has been set to user_a for all orders
        self.assertEqual(
            self.order_1.user_id,
            self.user_a,
            "The responsible should be set to the current user",
        )
        self.assertEqual(
            self.order_2.user_id,
            self.user_a,
            "The responsible should be set to the current user",
        )
        self.assertEqual(
            self.order_3.user_id,
            self.user_a,
            "The responsible should be set to the current user",
        )
        self.assertEqual(
            self.order_4.user_id,
            self.user_b,
            "The responsible should not change",
        )
        # print quotation as user_b
        self.order_1.with_user(self.user_b).print_quotation()
        self.order_2.with_user(self.user_b).print_quotation()
        self.order_3.with_user(self.user_b).print_quotation()
        self.order_4.with_user(self.user_b).print_quotation()
        # check that the responsible has not been changed
        self.assertEqual(self.order_1.user_id, self.user_a)
        self.assertEqual(self.order_2.user_id, self.user_a)
        self.assertEqual(self.order_3.user_id, self.user_a)
        self.assertEqual(self.order_4.user_id, self.user_b)
