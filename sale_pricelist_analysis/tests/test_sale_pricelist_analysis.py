# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestSalePricelistAnalysis(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_nothing(self):
        # this module only adds a menu entry, so nothing to test for now
        pass
