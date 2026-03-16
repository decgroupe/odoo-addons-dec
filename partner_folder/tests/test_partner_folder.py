# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestPartnerFolder(TransactionCase):
    """Test the partner_folder module."""

    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]

    def test_01_field_names(self):
        self.assertIn("folder_uri", self.partner_model._fields)
