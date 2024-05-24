# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from .common import TestSoftwareLicensePassActionViewCommon


class TestSoftwareLicensePassActionView(TestSoftwareLicensePassActionViewCommon):

    def test_01_software_license_pass_action_view(self):
        self._test_action_view_sm_records(self.model_software_license_pass)

    def test_02_software_license_pack_action_view_pass(self):
        pack_basic = self.env.ref("software_license_pass.sl_pack_basic")
        action = pack_basic.action_view_pass()
        self.assertEqual(action["domain"][0][2], pack_basic.pass_ids.ids)

    def test_03_software_license_pass_action_view_license(self):
        pass_mid1 = self.env.ref("software_license_pass.pass_mid1")
        action = pass_mid1.action_view_licenses()
        self.assertEqual(action["domain"][0][2], pass_mid1.license_ids.ids)

    def test_04_software_license_pass_action_view_hardwares(self):
        pass_mid1 = self.env.ref("software_license_pass.pass_mid1")
        action = pass_mid1.action_view_hardwares()
        self.assertEqual(action["domain"][0][2], pass_mid1.hardware_ids.ids)
