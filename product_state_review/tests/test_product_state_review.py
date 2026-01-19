# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestProductStateReview(TransactionCase):
    def setUp(self):
        super().setUp()
        # ref to [FURN_8855] Drawer
        self.product_drawer = self.env.ref("product.product_product_27")

    def test_01_(self):
        # check initial state
        self.assertEqual(self.product_drawer.state, "sellable")
        self.assertTrue(self.product_drawer.active)
        # set to review
        self.product_drawer.state = "review"
        self.assertEqual(self.product_drawer.state, "review")
        self.assertTrue(self.product_drawer.active)
        # set obsolete
        self.product_drawer.state = "obsolete"
        self.assertEqual(self.product_drawer.state, "obsolete")
        self.assertTrue(self.product_drawer.active)
        # back to normal
        self.product_drawer.state = "sellable"
        self.assertEqual(self.product_drawer.state, "sellable")
        self.assertTrue(self.product_drawer.active)
        # archive product
        self.product_drawer.action_archive()
        self.assertEqual(self.product_drawer.state, "obsolete")
        self.assertFalse(self.product_drawer.active)
        # reactivate product (state should remain obsolete)
        self.product_drawer.action_unarchive()
        self.assertEqual(self.product_drawer.state, "obsolete")
        self.assertTrue(self.product_drawer.active)
