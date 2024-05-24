# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

from odoo.addons.software_license_pass.tests.common import (
    TestSoftwareLicensePassActionViewCommon,
)


class TestSaleSoftwareLicensePassActionView(TestSoftwareLicensePassActionViewCommon):

    def setUp(self):
        super().setUp()
        self.premiumpass_so = self.env.ref("sale_software_license_pass.premiumpass_so")

    def test_01_action_view_pass(self):
        action_from_so = self.premiumpass_so.action_view_application_pass()
        action_from_pass = self.premiumpass_so.license_pass_ids.action_view()
        self.assertEqual(action_from_so, action_from_pass)
