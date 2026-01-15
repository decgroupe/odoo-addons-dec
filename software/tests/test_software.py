# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestSoftware(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_security_group_exists(self):
        group_id = self.env.ref("software.group_software_user")
        self.assertTrue(group_id.exists())
        group_id = self.env.ref("software.group_software_manager")
        self.assertTrue(group_id.exists())
        group_id = self.env.ref("software.group_software_supermanager")
        self.assertTrue(group_id.exists())
