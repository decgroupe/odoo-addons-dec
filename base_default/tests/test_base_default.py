# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

from odoo.tests.common import TransactionCase

_test_logger = logging.getLogger("odoo.tests")


class TestBaseDefault(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()

    def test_01_(self):
        pass
